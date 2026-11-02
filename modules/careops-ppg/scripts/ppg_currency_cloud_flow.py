"""Build a recurrence flow using existing solution connector references and bound assets."""
import copy


def build(seed, bindings):
    props = copy.deepcopy(seed["properties"])
    refs = props["connectionReferences"]
    props["connectionReferences"] = {k: refs[k] for k in ("shared_sharepointonline","shared_excelonlinebusiness")}
    d = props["definition"]
    d["triggers"] = {"Currency_schedule":{"type":"Recurrence","recurrence":{"frequency":"Minute","interval":15},
                                         "runtimeConfiguration":{"concurrency":{"runs":1}}}}
    actions = d["actions"] = {}
    def after(key):
        return {key:["Succeeded"]} if key else {}
    def http(uri, previous=None, method="GET", body=None, headers=None):
        parameters={"dataset":bindings["site"],"parameters/method":method,"parameters/uri":uri,
                    "parameters/headers":{"Accept":"application/json;odata=verbose",**(headers or {})}}
        if body is not None:
            parameters["parameters/body"]=body
        return {"type":"OpenApiConnection","runAfter":after(previous),"inputs":{
            "host":{"apiId":"/providers/Microsoft.PowerApps/apis/shared_sharepointonline","connectionName":"shared_sharepointonline","operationId":"HttpRequest"},
            "parameters":parameters}}
    previous=None
    for key,title,fields in [
        ("leads","PPG Source Update Leads","Id,Title,ObservationJSON,CurrencyNoticeText,CurrencyNoticeProvenance,CurrencyMatch,CurrencyPolicy,CurrencyOwner,CurrencyEvidence,CurrencyDisposition"),
        ("policies","PPG Catalogue","Id,DocumentUID,sourceDocumentId,sourceTitle,sourceCustodian"),
        ("relationships","PPG Document Relationships","FromDocumentUID,ToDocumentUID,RelationshipType,ReviewState")]:
        uri=f"_api/web/lists/getbytitle('{title}')/items?$select={fields}&$orderby=Id&$top=1500"
        for suffix,typ,value in [("rows","array",[]),("next","string",uri)]:
            name=key+"_"+suffix
            actions["init_"+name]={"type":"InitializeVariable","runAfter":after(previous),"inputs":{"variables":[{"name":name,"type":typ,"value":value}]}}
            previous="init_"+name
        read="read_"+key
        fields_map={f:"@item()?['"+f+"']" for f in fields.split(",")}
        if key=="leads":
            fields_map["odata.etag"]="@item()?['__metadata']?['etag']"
        inner={read:http("@variables('"+key+"_next')"),
               key+"_select":{"type":"Select","runAfter":after(read),"inputs":{"from":"@body('"+read+"')?['d']?['results']","select":fields_map}},
               key+"_merge":{"type":"Compose","runAfter":after(key+"_select"),"inputs":"@union(variables('"+key+"_rows'),body('"+key+"_select'))"},
               key+"_save":{"type":"SetVariable","runAfter":after(key+"_merge"),"inputs":{"name":key+"_rows","value":"@outputs('"+key+"_merge')"}},
               key+"_advance":{"type":"SetVariable","runAfter":after(key+"_save"),"inputs":{"name":key+"_next","value":"@replace(coalesce(body('"+read+"')?['d']?['__next'],''),'"+bindings["site"].replace("'","''")+"/','')"}}}
        actions["page_"+key]={"type":"Until","expression":"@empty(variables('"+key+"_next'))","limit":{"count":100,"timeout":"PT20M"},"operationOptions":"FailWhenLimitsReached","actions":inner,"runAfter":after(previous)}
        previous="page_"+key
    page="_api/web/lists/getbytitle('Site Pages')/items("+str(bindings["page"])+")"
    actions["coverage_page"]=http(page+"?$select=CanvasContent1",previous)
    actions["inputs_for_matcher"]={"type":"Compose","runAfter":after("coverage_page"),"inputs":{
        **{k:"@variables('"+k+"_rows')" for k in ("leads","policies","relationships")},
        "form":bindings["form"],"template":bindings["template"],"canvas":"@body('coverage_page')?['d']?['CanvasContent1']"}}
    actions["match_and_count"]={"type":"OpenApiConnection","runAfter":after("inputs_for_matcher"),"inputs":{
        "host":{"apiId":"/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness","operationId":"RunScriptProdV2","connectionName":"shared_excelonlinebusiness"},
        "parameters":{"source":bindings["site"],"scriptSource":bindings["site"],"drive":bindings["drive"],"scriptDrive":bindings["drive"],"file":bindings["book"],"scriptId":bindings["script"],"ScriptParameters/requestJson":"@string(outputs('inputs_for_matcher'))"}}}
    actions["plan"]={"type":"Compose","runAfter":after("match_and_count"),"inputs":"@json(body('match_and_count')?['result'])"}
    def patch(uri,body,etag):
        return http(uri,method="POST",body=body,headers={"X-HTTP-Method":"MERGE","If-Match":etag,"Content-Type":"application/json;odata=nometadata"})
    actions["write_candidates"]={"type":"Foreach","foreach":"@outputs('plan')?['writes']","runAfter":after("plan"),"operationOptions":"Sequential","actions":{
        "write_lead":patch("@concat('_api/web/lists/getbytitle(''PPG Source Update Leads'')/items(',string(item()?['id']),')')","@string(item()?['patch'])","@item()?['etag']")}}
    file="_api/web/GetFileByServerRelativePath(decodedurl='"+bindings["pagePath"].replace("'","''")+"')"
    actions["update_report"]={"type":"If","expression":"@equals(outputs('plan')?['changed'],true)","runAfter":after("write_candidates"),"actions":{
        "write_report":patch(page,"@string(setProperty(json('{}'),'CanvasContent1',outputs('plan')?['canvas']))","@body('coverage_page')?['d']?['__metadata']?['etag']")}}
    actions["read_draft"]=http(page+"?$select=CanvasContent1","update_report")
    actions["report_state"]=http(file+"?$select=Level,CheckOutType","read_draft")
    publish=http(file+"/Publish(comment='Currency coverage')",method="POST")
    checkin=http(file+"/CheckIn(comment='Currency coverage',checkintype=1)",method="POST")
    actions["verify_draft"]={"type":"If","runAfter":after("report_state"),
        "expression":"@equals(body('read_draft')?['d']?['CanvasContent1'],outputs('plan')?['canvas'])",
        "actions":{"publish_if_draft":{"type":"If","expression":"@not(equals(int(body('report_state')?['d']?['Level']),1))",
                   "actions":{"checkout_route":{"type":"If","expression":"@equals(int(body('report_state')?['d']?['CheckOutType']),2)",
                              "actions":{"publish":publish},"else":{"actions":{"major_checkin":checkin}}}}}},
        "else":{"actions":{"changed_draft":{"type":"Terminate","inputs":{"runStatus":"Failed","runError":{"code":"PageChanged","message":"Reconcile coverage draft"}}}}}}
    actions["final_page"]=http(file+"?$select=Level","verify_draft")
    actions["require_published"]={"type":"If","runAfter":after("final_page"),"expression":"@equals(int(body('final_page')?['d']?['Level']),1)",
        "actions":{"published_summary":{"type":"Compose","inputs":"@outputs('plan')?['summary']"}},
        "else":{"actions":{"publication_incomplete":{"type":"Terminate","inputs":{"runStatus":"Failed","runError":{"code":"Unpublished","message":"Coverage publication incomplete"}}}}}}
    return {**copy.deepcopy(seed),"properties":props}
