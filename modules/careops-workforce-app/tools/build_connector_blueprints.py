"""Build *unbound* SharePoint Standard connector operation templates, not enabled flows."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def http_action(method,uri,headers=None,body=None):
    parameters={"dataset":"__SHAREPOINT_SITE_ENV_VARIABLE__",
                "parameters/method":method,"parameters/uri":uri,
                "parameters/headers":headers or {"Accept":"application/json;odata=nometadata"}}
    if body is not None: parameters['parameters/body']=body
    return {"type":"OpenApiConnection","inputs":{"host":{
        "apiId":"/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
        "operationId":"HttpRequest","connectionName":"shared_sharepointonline"},
        "parameters":parameters},"runAfter":{}}


def build():
    uri="_api/web/lists/getbytitle('JP_PlanHeads')/items(@{variables('PlanItemId')})"
    data={
        "status":"unbound-template-disabled",
        "connector":"SharePoint Standard",
        "purpose":"Reference actions only; do NOT expose via a user-triggered privileged flow",
        "parameters_to_bind":["SharePoint site environment variable","PlanItemId from authorised server-side lookup",
           "ProposedHeadPayload after validated authorised transition"],
        "deployment_gates":["trusted actor resolver","SharePoint 412 and 429 tenant tests",
          "exact business version hash","server-side delegated authority and role expiry",
          "list and document library ACLs","native solution connection reference readback"],
        "actions":{
         "Read_Head":http_action('GET',uri),
         "CAS_Head":http_action('POST',uri,
            {"Accept":"application/json;odata=nometadata",
             "Content-Type":"application/json;odata=nometadata",
             "X-HTTP-Method":"MERGE",
             "IF-MATCH":"@body('Read_Head')?['@odata.etag']"},
            "@variables('ProposedHeadPayload')")
        },
        "critical_limitations":["Do not trust caller-provided operation ID, effective date or user identity",
            "Read_Head and CAS_Head alone do not implement transaction/compensation",
            "No retry-on-412 blind overwrite: revalidate state, role and expected generation",
            "Do not enable before identity/industrial/records/ACL tenant acceptance"]}
    out=ROOT/'flows'/'blueprints'/'sharepoint-cas-action-pair.json'
    out.write_text(json.dumps(data,indent=2)+'\n')
    return out
if __name__=='__main__':print(build())
