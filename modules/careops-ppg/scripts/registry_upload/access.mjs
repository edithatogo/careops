import { randomUUID } from "node:crypto";
// Exact list edit permission as represented by Power Automate's SharePoint run-only tab.
export async function ensureListAccess(adapter, settings, flowId, verifyOnly) {
  const base = '/flows/' + flowId;
  const version = '?api-version=2016-11-01';
  const delegate = {
    accessDefinition:{sharePointBasePermissions:[{high:0,low:15}]},
    delegationSource:{delegationService:'SharePoint',contractVersion:'2017-12-01'},
    delegatedAuthResource:{resourceCollection:settings.site.toLowerCase(),resourceId:settings.catalogueId}
  };
  async function inspect() {
    const result = await adapter.flow.get(base+'/permissions'+version);
    if (!Array.isArray(result.value) || result.nextLink || result['@odata.nextLink']) throw Error('Incomplete run-only permissions response');
    const scoped = result.value.map(x=>x.properties).filter(p=>{
      const target=p.authorizationDelegate?.delegatedAuthResource;
      return target?.resourceCollection?.toLowerCase()===delegate.delegatedAuthResource.resourceCollection &&
        target.resourceId?.toLowerCase()===settings.catalogueId.toLowerCase();
    });
    if (!scoped.length) return false;
    const [p] = scoped, d = p.authorizationDelegate, masks = d.accessDefinition?.sharePointBasePermissions;
    if (scoped.length !== 1 || p.permissionType !== 'AuthorizationDelegate' || p.roleName !== 'CanView' ||
        d.delegationSource?.delegationService !== 'SharePoint' || masks?.length !== 1 ||
        masks[0].high !== 0 || masks[0].low !== 15) throw Error('Catalogue delegation differs: inspect existing access');
    return true;
  }
  if (await inspect()) return 'verified';
  if (verifyOnly) throw Error('Missing Catalogue run-only access');
  await adapter.flow.send('POST',base+'/modifyPermissions'+version,
    {put:[{name:'DELEGATED-'+randomUUID(),properties:{roleName:'CanView',permissionType:'AuthorizationDelegate',authorizationDelegate:delegate}}]});
  if (!await inspect()) throw Error('Catalogue run-only grant did not persist');
  return 'created and verified';
}
