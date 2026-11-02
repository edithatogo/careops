// Read-only baseline for an existing Registry. The site and list bindings are supplied by the installer.
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';

const FILES_FIELD = 'Linked_x0020_PPG_x0020_files';
const READER = 'Files for a PPG registry record';
const CASE_FIELDS = ['Id', 'CaseUID', 'Title', 'Modified', 'OData__UIVersionString',
  'linkedDocumentUIDs', 'caseStatus', 'evidenceDraftLink', 'PPGRegistrySubmissionKey'];
const digest = data => createHash('sha256').update(data).digest('hex');
const odataText = value => encodeURIComponent(value.replaceAll("'", "''")).replaceAll("'", '%27');
const byId = (left, right) => left.id - right.id;

function requireValue(ok, message) {
  if (!ok) throw new Error('Registry preservation check: ' + message);
}

function listEndpoint(site, id) {
  requireValue(/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(id), 'invalid list ID');
  return site + "/_api/web/lists(guid'" + id + "')";
}

async function fileState(adapter, site, path, expectedRoot) {
  const root = expectedRoot.replace(/\/$/, '') + '/';
  requireValue(typeof path === 'string' && path.startsWith(root) &&
    !path.split('/').some(part => part === '.' || part === '..'), 'file outside the expected library or attachment folder');
  const endpoint = site + "/_api/web/GetFileByServerRelativePath(decodedurl='" + odataText(path) + "')";
  const meta = await adapter.read(endpoint + '?$select=UniqueId,UIVersionLabel,Length');
  const result = await adapter.request('GET', endpoint + '/$value', { responseType: 'arraybuffer' });
  requireValue(result instanceof ArrayBuffer || ArrayBuffer.isView(result), 'adapter must return binary file contents');
  const bytes = result instanceof ArrayBuffer ? Buffer.from(result) : Buffer.from(result.buffer, result.byteOffset, result.byteLength);
  requireValue(bytes.length === Number(meta.Length) && meta.UniqueId && meta.UIVersionLabel, 'file length or identity mismatch');
  return { fileId: meta.UniqueId, version: meta.UIVersionLabel, size: bytes.length, sha256: digest(bytes) };
}

async function readEditions(adapter, settings, site, record, uid) {
  const library = listEndpoint(site, settings.libraryId);
  const view = await adapter.read(library + "/views/getbytitle('" + odataText(READER) + "')?$select=Id,ServerRelativeUrl");
  const link = new URL(record[FILES_FIELD]);
  requireValue(link.origin === new URL(site).origin && decodeURIComponent(link.pathname) === view.ServerRelativeUrl &&
    link.searchParams.get('FilterField1') === 'PPGDocumentUID' && link.searchParams.get('FilterValue1') === uid,
    'record link does not point to its own evidence view');
  const endpoint = library + '/RenderListDataAsStream?View=' + encodeURIComponent(view.Id) + '&' + link.searchParams;
  const ids = new Set();
  const pages = new Set();
  const editions = [];
  let paging;
  do {
    const data = await adapter.request('POST', endpoint, {
      data: { parameters: { RenderOptions: 2, ...(paging ? { Paging: paging } : {}) } },
      headers: { 'Content-Type': 'application/json;odata=nometadata' }
    });
    const page = typeof data === 'string' ? JSON.parse(data) : data;
    requireValue(Array.isArray(page.Row), 'file view did not return rows');
    for (const row of page.Row) {
      const id = Number(row.ID);
      requireValue(row.PPGDocumentUID === uid && Number.isSafeInteger(id) && id > 0 && !ids.has(id), 'unexpected or duplicate linked file');
      ids.add(id);
      editions.push({ id, edition: row.PPGPolicyEdition, kind: row.PPGCaptureKind, pathHash: digest(row.FileRef),
        file: await fileState(adapter, site, row.FileRef, settings.libraryRoot) });
    }
    paging = page.NextHref?.replace(/^\?/, '');
    if (paging) {
      requireValue(!pages.has(paging), 'repeated file-view page');
      pages.add(paging);
    }
  } while (paging);
  return editions.sort(byId);
}

async function readCases(adapter, settings, site, uid) {
  const queue = listEndpoint(site, settings.queueId);
  const cases = [];
  let cursor = 0;
  const top = 250;
  while (true) {
    const page = await adapter.read(queue + '/items?$orderby=Id&$top=' + top +
      '&$filter=Id%20gt%20' + cursor + '&$select=' + CASE_FIELDS.join(','));
    requireValue(Array.isArray(page.value), 'review queue did not return rows');
    for (const row of page.value) {
      const id = Number(row.Id);
      requireValue(Number.isSafeInteger(id) && id > cursor, 'invalid review queue pagination');
      cursor = id;
      if (!row.linkedDocumentUIDs?.includes(uid) && !row.PPGRegistrySubmissionKey?.startsWith(uid + '/')) continue;
      requireValue(JSON.parse(row.linkedDocumentUIDs).includes(uid), 'submission key and case document identity disagree');
      const response = await adapter.read(queue + '/items(' + id + ')/AttachmentFiles');
      requireValue(Array.isArray(response.value) && !response['odata.nextLink'] && !response['@odata.nextLink'], 'incomplete case attachments');
      const attachments = [];
      for (const a of response.value) {
        const folder = settings.queueRoot.replace(/\/$/, '') + '/Attachments/' + id;
        attachments.push({ nameHash: digest(a.FileName), file: await fileState(adapter, site, a.ServerRelativeUrl, folder) });
      }
      attachments.sort((a,b) => a.nameHash.localeCompare(b.nameHash));
      cases.push({ id, caseUid: row.CaseUID, version: row.OData__UIVersionString,
        fieldsHash: digest(JSON.stringify(CASE_FIELDS.map(key => row[key] ?? null))), attachments });
    }
    if (!page.value.length || page.value.length < top && !page['odata.nextLink'] && !page['@odata.nextLink']) break;
  }
  return cases.sort(byId);
}

/** Snapshot an already installed record through its native reader and its Review Queue. */
export async function capturePreservation({ adapter, settings, recordId }) {
  const id = Number(recordId);
  requireValue(Number.isSafeInteger(id) && id > 0, 'invalid Registry item ID');
  const site = settings.site.replace(/\/$/, '');
  const url = listEndpoint(site, settings.catalogueId) + '/items(' + id + ')?$select=Id,DocumentUID,' + FILES_FIELD;
  const record = await adapter.read(url);
  requireValue(record.Id === id && record.DocumentUID && record[FILES_FIELD], 'requires an existing installed Registry record with a direct files link');
  const [editions, cases] = await Promise.all([
    readEditions(adapter, settings, site, record, record.DocumentUID),
    readCases(adapter, settings, site, record.DocumentUID)
  ]);
  requireValue(editions.length > 0 && cases.length > 0, 'select a record with at least one linked edition and one review case');
  return { site, registry: settings.catalogueId, recordId: id, uid: record.DocumentUID,
    library: settings.libraryId, queue: settings.queueId, recordLinkHash: digest(record[FILES_FIELD]), editions, cases };
}

/** A mismatch aborts the deployment check without printing private record contents. */
export function comparePreservation(before, after) {
  requireValue(isDeepStrictEqual(before, after), 'record files, edition metadata, case fields or attachments changed');
  return { recordId: before.recordId, editionIds: before.editions.map(row => row.id), caseIds: before.cases.map(row => row.id),
    snapshotSha256: digest(JSON.stringify(before)) };
}
