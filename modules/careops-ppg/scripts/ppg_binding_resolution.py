"""Resolve remaining SharePoint connector actions against private native identities."""
import re
from urllib.parse import unquote, urlsplit

FILE_ID = re.compile(r"GetFileById\('+([0-9a-f-]{36})'+\)", re.I)
FOLDER = re.compile(r"Get(?:File|Folder)ByServerRelativePath\(decodedurl='+(/[^']*)(?:'+\)|/',)", re.I)
BODY = re.compile(r"(?:first\(body\('([^']+)'\)\?\['value'\]\)|body\('([^']+)'\))\?\['(UniqueId|ServerRelativeUrl)'\]")


def action_binding(name, actions, environment, proof, seen=()):
    """Return (target IDs, directions), or None when the location depends on input."""
    if name in seen or name not in actions:
        return None
    inp = actions[name]['inputs']
    if not isinstance(inp, dict) or 'sharepointonline' not in str(inp.get('host', {})).lower():
        return None
    op = inp['host'].get('operationId')
    p = inp.get('parameters', {})
    site = p.get('dataset', '')
    var = re.fullmatch(r"@\{?parameters\('([^']+)'\)\}?", site)
    site = environment.get(var[1], '') if var else site
    site = site.rstrip('/').lower()
    route = p.get('parameters/uri', p.get('path', ''))
    method = p.get('parameters/method', '')
    directions = ('ReadFlows',) if method == 'GET' or op in ('GetFileContentByPath','GetFileMetadataByPath') else ('WriteFlows',)
    if method.startswith('@'):
        if not re.fullmatch(r"@if\(equals\(outputs\('[^']+'\)\?\['statusCode'\],404\),'POST','GET'\)", method):
            return None
        directions = ('ReadFlows','WriteFlows')
    if not method and op not in ('MoveFileAsync','CreateFile','GetFileContentByPath','GetFileMetadataByPath'):
        return None
    def folder_id(path):
        path = unquote(path).lower().rstrip('/')
        return next((key for key, root in proof['folders'].items()
                     if path == root.lower() or path.startswith(root.lower().rstrip('/')+'/')), None)
    def previous(source):
        result = action_binding(source, actions, environment, proof, (*seen,name))
        return result[0] if result else set()
    if site != proof['site'].lower().rstrip('/'):
        return None
    if op == 'MoveFileAsync':
        src = re.fullmatch(r"@body\('([^']+)'\)\?\['Id'\]", p.get('parameters/sourceFileId',''))
        dst = p.get('parameters/destinationFolderPath','')
        if not src or not dst.startswith('/') or '@' in dst or p.get('parameters/destinationDataset','').lower().rstrip('/') != site:
            return None
        source = previous(src[1])
        dest = folder_id(urlsplit(site).path + dst)
        if source and dest:
            return (source | {dest}, ('WriteFlows',))
        return None
    if op == 'CreateFile':
        folder = p.get('folderPath','').split('@',1)[0]
        ident = folder_id(urlsplit(site).path + folder)
        return ({ident}, directions) if ident else None
    literals = FILE_ID.findall(route)
    if literals and len(literals) == route.lower().count('getfilebyid('):
        ids = {proof['files'].get(v.lower()) for v in literals}
        return (ids,directions) if None not in ids else None
    paths = FOLDER.findall(route)
    calls = len(re.findall(r'Get(?:File|Folder)ByServerRelativePath\(',route,re.I))
    if paths and len(paths)==calls and 'getfilebyid(' not in route.lower():
        ids = {folder_id(path) for path in paths}
        return (ids,directions) if None not in ids else None
    # A filter of a literal profile array can only return those configured files.
    profile = re.match(r"^@concat\('_api/web/GetFileById\(',decodeUriComponent\('%27'\),outputs\('([^']+)'\)\?\['UniqueId'\],decodeUriComponent\('%27'\),", route)
    if profile:
        selected = actions.get(profile[1], {})
        first = re.fullmatch(r"@first\(body\('([^']+)'\)\)", str(selected.get('inputs', '')))
        query = actions.get(first[1], {}) if first and selected.get('type') == 'Compose' else {}
        source = re.fullmatch(r"@outputs\('([^']+)'\)", query.get('inputs', {}).get('from', '')) if query.get('type') == 'Query' else None
        configured = actions.get(source[1], {}) if source else {}
        profiles = configured.get('inputs')
        if configured.get('type') == 'Compose' and isinstance(profiles, list) and profiles:
            ids = {proof['files'].get(str(v.get('UniqueId','')).lower()) if isinstance(v,dict) else None for v in profiles}
            if None not in ids:
                return ids, directions
    # A connector-returned UniqueId or ServerRelativeUrl identifies the same file
    # or one enumerated by its parent folder. Arbitrary JSON fields do not.
    refs = BODY.findall(route)
    if len(refs)==1 and (route.startswith("@substring(body(") or route.startswith("@concat('_api/web/GetFileById(")):
        direct, other, field = refs[0]
        if route.count("body('")==1 and 'outputs(' not in route and 'if(' not in route:
            ids = previous(direct or other)
            if ids:
                return ids,directions
    return None
