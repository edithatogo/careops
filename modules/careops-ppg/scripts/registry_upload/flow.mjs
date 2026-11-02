import { readFileSync } from 'node:fs';
import { isDeepStrictEqual } from 'node:util';

const template = readFileSync(new URL('./flow-template.json', import.meta.url), 'utf8');
const version = '?api-version=2016-11-01';
const connector = 'shared_sharepointonline';
const apiId = '/providers/Microsoft.PowerApps/apis/' + connector;
const uuid = /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i;
const invokerAuth = {
  type: 'Raw',
  value: "@json(decodeBase64(triggerOutputs().headers['X-MS-APIM-Tokens']))['$ConnectionKey']",
};

function requireGuid(value, label) {
  if (typeof value !== 'string' || !uuid.test(value)) throw Error('Expected a GUID for ' + label);
  return value;
}

function checkInputs(settings) {
  const site = new URL(settings.site);
  if (site.protocol !== 'https:' || site.username || site.password ||
      site.search || site.hash || site.href.replace(/\/$/, '') !== settings.site) {
    throw Error('Expected a canonical HTTPS site URL without a trailing slash');
  }
  for (const root of [settings.libraryRoot, settings.queueRoot]) {
    const prefix = decodeURIComponent(site.pathname).replace(/\/$/, '') + '/';
    if (!root?.startsWith(prefix) || root.endsWith('/') || root.includes('//') ||
        root.split('/').some(part => part === '.' || part === '..') ||
        /['%?#\\{}\x00-\x1f]/u.test(root)) {
      throw Error('Expected an unencoded server-relative folder inside the target site');
    }
  }
  for (const key of ['catalogueId', 'queueId', 'libraryId']) requireGuid(settings[key], key);
  if (new Set([settings.catalogueId, settings.queueId, settings.libraryId].map(x => x.toLowerCase())).size !== 3) {
    throw Error('The catalogue, queue and library must be distinct');
  }
  if (!/^[a-z0-9_-]+$/i.test(settings.connectionName ?? '')) throw Error('Invalid connection name');
  if (!settings.displayName?.trim() || /[\x00-\x1f]/u.test(settings.displayName)) throw Error('Invalid flow display name');
  return site;
}

export function buildFlow(settings) {
  const site = checkInputs(settings);
  const bindings = {
    SITE: settings.site, ORIGIN: site.origin,
    CATALOGUE_ID: settings.catalogueId, QUEUE_ID: settings.queueId,
    LIBRARY_ROOT: settings.libraryRoot, QUEUE_ROOT: settings.queueRoot,
    ENCODED_SUBMISSION_FOLDER: encodeURIComponent(settings.libraryRoot + '/Registry review submissions'),
  };
  // Substitute while parsing so paths containing quotes remain literal JSON strings.
  const definition = JSON.parse(template, (_key, value) =>
    typeof value === 'string' ? value.replace(/\{\{([A-Z_]+)\}\}/g, (_token, key) => {
      if (!Object.hasOwn(bindings, key)) throw Error('Unknown workflow binding ' + key);
      return bindings[key];
    }) : value);
  return { properties: {
    displayName: settings.displayName, definition,
    connectionReferences: { [connector]: { id: apiId, source: 'Invoker', connectionName: settings.connectionName } },
    state: 'Stopped', flowFailureAlertSubscribed: false,
  } };
}

function normalizeDefinition(definition) {
  // The service adds this precise invocation expression to SharePoint actions.
  // Preserve any other authentication or action change as a real conflict.
  const result = structuredClone(definition);
  function visit(actions) {
    for (const action of Object.values(actions ?? {})) {
      if (action.type === 'OpenApiConnection' && action.inputs?.host?.apiId === apiId &&
          isDeepStrictEqual(action.inputs.authentication, invokerAuth)) delete action.inputs.authentication;
      visit(action.actions);
      visit(action.else?.actions);
    }
  }
  visit(result?.actions);
  return result;
}

function verifyIdentity(flow, id, expected) {
  const p = flow?.properties;
  const refs = p?.connectionReferences ?? {};
  const ref = refs[connector];
  if (flow?.name !== id || p?.displayName !== expected.displayName ||
      !isDeepStrictEqual(Object.keys(refs), [connector]) ||
      !ref || ref.id !== apiId || ref.source !== 'Invoker' ||
      ref.connectionName !== expected.connectionReferences[connector].connectionName ||
      !isDeepStrictEqual(normalizeDefinition(p.definition), expected.definition)) {
    throw Error('Workflow definition or destination binding differs; reconcile before deploying');
  }
  return p;
}

async function findFlow(api, settings) {
  if (settings.flowId) return requireGuid(settings.flowId, 'flowId');
  const quoted = settings.displayName.replaceAll("'", "''");
  const filter = encodeURIComponent("search('" + quoted + "')");
  const page = await api.get('/flows' + version + '&$filter=' + filter);
  if (!Array.isArray(page?.value) || page.nextLink || page['@odata.nextLink']) {
    throw Error('Incomplete flow discovery; provide an exact flowId');
  }
  const matches = page.value.filter(f => f.properties?.displayName === settings.displayName);
  if (matches.length > 1) throw Error('Ambiguous display name; provide an exact flowId');
  return matches.length ? requireGuid(matches[0].name, 'discovered flow') : undefined;
}

export async function ensureFlow(adapter, settings, { verifyOnly = false } = {}) {
  const desired = buildFlow(settings);
  const api = adapter.flow;
  const changes = [];
  let flowId = await findFlow(api, settings);
  if (!flowId) {
    if (verifyOnly) throw Error('Workflow missing');
    const created = await api.send('POST', '/flows' + version, desired);
    flowId = requireGuid(created?.name, 'created flow');
    changes.push('created workflow');
  }
  const path = '/flows/' + flowId;
  const read = async () => verifyIdentity(await api.get(path + version), flowId, desired.properties);
  let current = await read();
  if (!['Started', 'Stopped'].includes(current.state)) throw Error('Unexpected workflow state');
  if (current.flowFailureAlertSubscribed !== false) {
    if (verifyOnly || current.flowFailureAlertSubscribed !== true) throw Error('Owner alert state is unverified or enabled');
    await api.send('POST', path + '/unsubscribeFlowFailureAlerts' + version, {});
    current = await read();
    if (current.flowFailureAlertSubscribed !== false) throw Error('Owner alert readback differs');
    changes.push('disabled owner failure alerts');
  }
  if (current.state === 'Stopped') {
    if (verifyOnly) throw Error('Workflow is stopped');
    await api.send('POST', path + '/start' + version, {});
    current = await read();
    changes.push('started workflow');
  }
  if (current.state !== 'Started' || current.flowFailureAlertSubscribed !== false) {
    throw Error('Workflow activation or owner alert readback differs');
  }
  return { flowId, changes };
}
