// SharePoint additions to an existing installation of the PPG workbench.
// Each write is preceded by a native state check and followed by a readback.
import assert from 'node:assert/strict';
import { isDeepStrictEqual } from 'node:util';

const GUID = /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i;
const READER = 'Files for a PPG registry record';
const FOLDER = 'Registry review submissions';
const KIND = 'Review submission';
const KEY = 'PPGRegistrySubmissionKey';
const UPLOAD = 'Upload updated PPG';
const LINK = 'Linked PPG files';
const COLUMNS = ['DocIcon', 'LinkFilename', 'PPGOriginalFilename', 'PPGPolicyEdition',
  'PPGCurrency', 'PPGCaptureKind', 'PPGDocumentUID'];
const LINK_FORMAT = { elmType: 'a', attributes: { href: '@currentField', target: '_blank',
  title: 'Open the files linked to this registry record' }, txtContent: 'Open linked files' };
const MERGE = { 'X-HTTP-Method': 'MERGE' };
const xml = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const fieldPath = (list, name) => list + "/fields/getbyinternalnameortitle('" + name + "')";
const encodedPath = path => path.split('/').map(encodeURIComponent).join('/');
const normalizeFormula = value => value.replace(/\[DocumentUID\]$/, 'DocumentUID');

async function checkWorkloadFields(read, list, required) {
  const filter = Object.keys(required).map(name => "InternalName eq '" + name + "'").join(' or ');
  const fields = await read(list + '/fields?$select=InternalName,TypeAsString&$filter=' + filter);
  const actual = Object.fromEntries(fields.value.map(f => [f.InternalName, f.TypeAsString]));
  assert.deepEqual(actual, required, 'Base workbench fields missing or incompatible');
}

function single(values, predicate, description) {
  const matches = values.filter(predicate);
  assert(matches.length <= 1, 'Ambiguous ' + description);
  return matches[0];
}

function queryFor(folder) {
  const ref = name => '<FieldRef Name="' + name + '" />';
  const compare = (op, name, type, value) =>
    '<' + op + '>' + ref(name) + '<Value Type="' + type + '">' + xml(value) + '</Value></' + op + '>';
  const archived = '<And>' + compare('BeginsWith', 'FileDirRef', 'Text', folder + '/Captured Policy Archive') +
    '<IsNotNull>' + ref('PPGCaptureSHA256') + '</IsNotNull></And>';
  const submitted = '<And>' + compare('Eq', 'FileDirRef', 'Text', folder + '/' + FOLDER) +
    compare('Eq', 'PPGCaptureKind', 'Choice', KIND) + '</And>';
  const ordered = '</Where><OrderBy>' + ref('ID') + '</OrderBy>';
  return { current: '<Where><Or>' + archived + submitted + '</Or>' + ordered,
    legacy: '<Where>' + archived + ordered };
}

function uploadFormat(flowId) {
  assert(GUID.test(flowId), 'Registry phase requires the deployed flow ID');
  return { elmType: 'button', attributes: { class: 'ms-fontColor-themePrimary',
    title: 'Select a file to submit an updated PPG for review' },
  style: { cursor: 'pointer', border: 'none', background: 'transparent', 'text-align': 'left' },
  txtContent: UPLOAD, customRowAction: { action: 'executeFlow', actionParams: JSON.stringify({
    id: flowId, headerText: UPLOAD, runFlowButtonText: 'Submit for review' }) } };
}

function footerFor(path) {
  return { elmType: 'div', style: { display: "=if([$ID] > 0, 'block', 'none')", padding: '8px 0' },
    children: [{ elmType: 'a', attributes: { href: "='" + encodedPath(path).replaceAll("'", "''") +
      "?FilterField1=ID&FilterValue1=' + [$ID]", target: '_self', title: 'Open this record’s upload action' },
    txtContent: 'Upload updated PPG for this record' }] };
}

function conditionalMerge(resource) {
  const etag = resource.registryResponseETag ?? resource['@odata.etag'] ?? resource['odata.etag'];
  assert(typeof etag === 'string' && /^(W\/)?"[^"\r\n]+"$/.test(etag), 'Shared metadata update requires an exact ETag; reconcile this setting in SharePoint');
  return { ...MERGE, 'If-Match': etag };
}

async function provisionData({ read, change, lib, queue, api, root }) {
  const choicesPath = fieldPath(lib, 'PPGCaptureKind');
  const getKind = () => read(choicesPath + '?$select=TypeAsString,Choices');
  const kind = await getKind();
  assert.equal(kind.TypeAsString, 'Choice');
  assert(kind.Choices.includes('Document') && kind.Choices.includes('Supporting source page'), 'Capture choices conflict');
  if (!kind.Choices.includes(KIND)) {
    const choices = [...kind.Choices, KIND];
    await change('add-review-choice', choicesPath, { Choices: choices }, conditionalMerge(kind));
    assert.deepEqual((await getKind()).Choices, choices);
  }

  const folder = root + '/' + FOLDER;
  const folders = await read(lib + "/RootFolder/Folders?$select=Name&$filter=Name eq 'Registry review submissions'");
  if (!folders.value.some(entry => entry.Name === FOLDER)) {
    await change('create-review-folder', api + '/folders', { ServerRelativeUrl: folder });
  }
  const folderUrl = api + "/GetFolderByServerRelativePath(decodedurl='" +
    encodeURIComponent(folder.replaceAll("'", "''")) + "')";
  assert.equal((await read(folderUrl + '?$select=ServerRelativeUrl')).ServerRelativeUrl, folder);

  const existing = await read(queue + "/fields?$select=InternalName,Title&$filter=InternalName eq '" + KEY +
    "' or Title eq '" + KEY + "'");
  if (!existing.value.length) {
    const schema = '<Field Type="Text" Name="' + KEY + '" StaticName="' + KEY + '" DisplayName="' + KEY +
      '" MaxLength="180" Indexed="TRUE" EnforceUniqueValues="TRUE" Required="FALSE" ShowInNewForm="FALSE" ShowInEditForm="FALSE" />';
    await change('create-submission-key', queue + '/fields/CreateFieldAsXml', { parameters: { SchemaXml: schema, Options: 0 } });
  } else {
    assert(existing.value.length === 1 && existing.value[0].InternalName === KEY, 'Submission key field conflict');
  }
  const key = await read(fieldPath(queue, KEY) + '?$select=TypeAsString,Required,Indexed,EnforceUniqueValues,MaxLength');
  assert(key.TypeAsString === 'Text' && !key.Required && key.Indexed && key.EnforceUniqueValues && key.MaxLength >= 180,
    'Existing submission key does not meet uniqueness, length or type requirements');

  const indexPath = fieldPath(lib, 'PPGDocumentUID');
  const index = await read(indexPath + '?$select=Indexed,TypeAsString');
  assert.equal(index.TypeAsString, 'Text');
  if (!index.Indexed) {
    await change('index-document-uid', indexPath, { Indexed: true }, MERGE);
    assert.equal((await read(indexPath + '?$select=Indexed')).Indexed, true);
  }
  return folder;
}

async function ensureColumns({ read, change }, view, columns, stage) {
  const path = view + '/ViewFields';
  const existing = (await read(path)).Items;
  const missing = columns.filter(column => !existing.includes(column));
  for (const column of missing) {
    assert(/^[\w]+$/.test(column), 'Unsafe column name');
    await change(stage + '-' + column, path + "/AddViewField('" + column + "')");
  }
  if (missing.length) assert.deepEqual((await read(path)).Items, [...existing, ...missing], 'View columns changed concurrently');
}

async function ensureReader(ctx) {
  const { lib, root, read, change } = ctx;
  const query = queryFor(root);
  const path = lib + "/views/getbytitle('" + READER + "')";
  const select = '?$select=Id,Title,ViewQuery,Scope,ServerRelativeUrl,PersonalView,Paged,RowLimit';
  const found = await read(lib + '/views' + select + "&$filter=Title eq '" + READER + "'");
  let view = single(found.value, v => v.Title === READER, READER);
  if (!view) {
    await change('create-linked-view', lib + '/views/add', { parameters: { Title: READER,
      ViewFields: COLUMNS, Query: query.current, PersonalView: false, SetAsDefaultView: false,
      RowLimit: 50, Paged: true, ViewTypeKind: 1 } });
    view = await read(path + select);
  }
  assert(!view.PersonalView && view.Paged && view.RowLimit === 50 &&
    view.ServerRelativeUrl.startsWith(root + '/Forms/'), 'Incompatible linked file view');
  assert([query.legacy, query.current].includes(view.ViewQuery), 'Linked file view query drift');
  assert([0, 1].includes(view.Scope), 'Linked file view scope drift');
  if (view.ViewQuery !== query.current || view.Scope !== 1) {
    await change('configure-linked-view', path, { ViewQuery: query.current, Scope: 1 }, MERGE);
    view = await read(path + select);
  }
  assert(view.ViewQuery === query.current && view.Scope === 1, 'Linked view readback failed');
  await ensureColumns(ctx, path, COLUMNS, 'linked-view-column');
  return view;
}

async function calculatedField(ctx, { title, name, formula, formatter }) {
  const { cat, read, change } = ctx;
  const existing = await read(cat + "/fields?$select=Title,InternalName,StaticName&$filter=Title eq '" +
    title + "' or StaticName eq '" + name + "' or InternalName eq '" + name + "'");
  const match = single(existing.value, () => true, title);
  if (!match) {
    const schema = '<Field Type="Calculated" ResultType="Text" Name="' + name + '" StaticName="' + name +
      '" DisplayName="' + title + '" ReadOnly="TRUE" ShowInDisplayForm="TRUE" CustomFormatter="' +
      xml(JSON.stringify(formatter)) + '"><Formula>' + xml(formula) +
      '</Formula><FieldRefs><FieldRef Name="DocumentUID"/></FieldRefs></Field>';
    await change('create-' + name, cat + '/fields/CreateFieldAsXml', { parameters: { SchemaXml: schema, Options: 0 } });
  } else {
    assert(match.Title === title && match.StaticName === name, title + ' field identity conflict');
  }
  const field = await read(fieldPath(cat, title) + '?$select=Title,InternalName,StaticName,TypeAsString,Formula,CustomFormatter');
  assert(field.Title === title && field.StaticName === name && field.TypeAsString === 'Calculated' &&
    normalizeFormula(field.Formula) === normalizeFormula(formula) &&
    isDeepStrictEqual(JSON.parse(field.CustomFormatter), formatter), title + ' formula or formatter drift');
  return field.InternalName;
}

async function ensureFooter(ctx, path) {
  const { cat, read, change } = ctx;
  const types = await read(cat + "/contenttypes?$select=Id,Name&$filter=Name eq 'Item'");
  const item = single(types.value, t => t.Name === 'Item', 'Registry Item content type');
  assert(/^0x[0-9a-f]+$/i.test(item?.Id.StringValue ?? ''), 'Missing Item content type');
  const endpoint = cat + "/contenttypes('" + item.Id.StringValue + "')";
  const get = () => read(endpoint + '?$select=ClientFormCustomFormatter,ReadOnly,Sealed');
  const initial = await get();
  const format = JSON.parse(initial.ClientFormCustomFormatter || '{}');
  const footer = footerFor(path);
  if (format.footerJSONFormatter) {
    assert.deepEqual(format.footerJSONFormatter, footer, 'Custom Registry footer needs reconciliation');
    return;
  }
  assert(!initial.ReadOnly && !initial.Sealed, 'Registry content type is locked');
  const desired = { ...format, footerJSONFormatter: footer };
  await change('add-registry-footer', endpoint, { ClientFormCustomFormatter: JSON.stringify(desired) }, conditionalMerge(initial));
  assert.deepEqual(JSON.parse((await get()).ClientFormCustomFormatter), desired);
}

export async function applySharePoint({ settings, read, write, phase, verifyOnly = false }) {
  const { site, catalogueId, queueId, libraryId, flowId } = settings;
  assert([catalogueId, queueId, libraryId].every(id => GUID.test(id)) &&
    new Set([catalogueId, queueId, libraryId].map(id => id.toLowerCase())).size === 3, 'Three distinct list GUIDs required');
  assert(['prerequisites', 'registry'].includes(phase), 'Unknown installation phase');
  const base = new URL(site);
  assert(base.protocol === 'https:' && !base.search && !base.hash && !base.username && !base.password, 'Invalid site');
  const api = site.replace(/\/$/, '') + '/_api/web';
  const endpoint = id => api + "/lists(guid'" + id + "')";
  const cat = endpoint(catalogueId), queue = endpoint(queueId), lib = endpoint(libraryId);
  const meta = await read(lib + '?$select=Id,BaseType,EnableVersioning,RootFolder/ServerRelativeUrl&$expand=RootFolder');
  const root = meta.RootFolder.ServerRelativeUrl;
  assert(meta.Id.toLowerCase() === libraryId.toLowerCase() && meta.BaseType === 1 && meta.EnableVersioning &&
    root.startsWith(decodeURIComponent(base.pathname).replace(/\/$/, '') + '/'), 'Expected a versioned evidence library on the pinned site');
  const changes = [];
  async function change(label, url, data, headers = {}) {
    assert(!verifyOnly, 'Missing or outdated SharePoint component: ' + label);
    await write(label, url, data, headers);
    changes.push(label);
  }
  const ctx = { read, change, api, lib, queue, cat, root };
  if (phase === 'prerequisites') {
    const [queueMeta] = await Promise.all([
      read(queue + '?$select=EnableAttachments'),
      checkWorkloadFields(read, cat, { DocumentUID: 'Text', sourceDocumentId: 'Note', sourceTitle: 'Note' }),
      checkWorkloadFields(read, queue, { CaseUID: 'Text', linkedDocumentUIDs: 'Note', caseStatus: 'Text',
        nextAction: 'Note', evidenceDraftLink: 'Note', sourceBaselineRef: 'Note' }),
      checkWorkloadFields(read, lib, { PPGDocumentUID: 'Text', PPGOriginalFilename: 'Text', PPGPolicyEdition: 'Text',
        PPGCurrency: 'Choice', PPGCaptureKind: 'Choice', PPGCaptureSHA256: 'Text', PPGCaptureEditionEvidence: 'Note' }),
    ]);
    assert(queueMeta.EnableAttachments, 'Review Queue attachments must be enabled');
    const folder = await provisionData(ctx);
    const reader = await ensureReader(ctx);
    return { changes, folder, linkedView: reader.ServerRelativeUrl };
  }
  const reader = await ensureReader({ ...ctx, change: async () => { throw Error('Run prerequisites before Registry setup'); } });
  const target = base.origin + encodedPath(reader.ServerRelativeUrl) + '?FilterField1=PPGDocumentUID&FilterValue1=';
  const readerField = await calculatedField(ctx, { title: LINK, name: 'PPGRegistryFiles',
    formula: '="' + target + '"&[DocumentUID]', formatter: LINK_FORMAT });
  const uploadField = await calculatedField(ctx, { title: UPLOAD, name: 'PPGRegistryUpdate',
    formula: '=[DocumentUID]', formatter: uploadFormat(flowId) });
  const registryView = (await read(cat + '/DefaultView?$select=ServerRelativeUrl')).ServerRelativeUrl;
  await ensureColumns(ctx, cat + '/DefaultView', [readerField, uploadField], 'registry-view-column');
  await ensureFooter(ctx, registryView);
  return { changes, registryView, linkedView: reader.ServerRelativeUrl, readerField, uploadField };
}
