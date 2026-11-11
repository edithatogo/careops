"""Generate reviewable (NOT round-trip validated) Power Apps YAML and flow specs.

Native app/solution components must be bound and exported by Power Apps Studio.
"""
from pathlib import Path
import json
import yaml
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'canvas'/'Src'; FLOWS=ROOT/'flows'
SRC.mkdir(parents=True,exist_ok=True);FLOWS.mkdir(exist_ok=True)

def label(name,formula,y):return {name:{'Control':'Label@2.5.1','Properties':{'Text':formula,'X':'=24','Y':f'={y}','Width':'=920','Height':'=42','Size':'=16'}}}
def button(name,text,formula,y,x=24):return {name:{'Control':'Button@0.0.45','Properties':{'Text':'='+json.dumps(text),'OnSelect':formula,'X':f'={x}','Y':f'={y}','Width':'=220','Height':'=42','AccessibleLabel':'='+json.dumps(text)}}}
def gallery(name,items,y):return {name:{'Control':'Gallery@2.15.0','Variant':'Vertical','Properties':{'Items':items,'X':'=24','Y':f'={y}','Width':'=920','Height':'=260','TemplateSize':'=64'},'Children':[label('ItemCaption','=ThisItem.Title',8)]}}
# All source is a maker-reviewable design. True .pa.yaml files must ultimately be
# exported from a real Power Apps instance using the current authoring version.
screens={
 'Home': [label('Welcome','= "Medical job planning — Workforce"',24),button('MyPlans','My job plans','=Navigate(PractitionerDashboard)',100),button('MyApprovals','My approvals','=Navigate(ApproverDashboard)',160),button('Administration','Operations','=Navigate(OperatorDashboard)',220)],
 'PractitionerDashboard':[label('Title','= "My job plans"',20),gallery('MyPlansList',"=Filter(JP_PlanHeads, OwnerUPN = User().Email)",90),button('NewRevision','Start revision','=Navigate(PlanEditor)',390),button('Versions','Version history','=Navigate(VersionHistory)',450),button('Back','Home','=Navigate(Home)',515)],
 'ApproverDashboard':[label('Title','= "Assigned reviews"',20),gallery('AssignedReviews',"=Filter(JP_ReviewTasks, AssignedToUPN = User().Email && Status = \"Open\")",90),button('OpenCase','Inspect selected case','=Navigate(ReviewCase)',390),button('Back','Home','=Navigate(Home)',450)],
 'PlanEditor':[label('Title','= "Proposed job-plan revision"',20),label('DraftStatus','= "Drafts are not submitted for approval until you choose Submit"',80),gallery('Sessions',"=Filter(JP_PlanSessions, DraftKey = varDraftKey)",135),button('SaveDraft','Save draft','=Notify("Draft is not persisted: connect the authorised SaveDraft flow before use.",NotificationType.Information)',430),button('ExplicitSubmit','Submit for consultation','=Set(varSubmitConfirmed,true); Navigate(SubmitConfirmation)',485)],
 'SubmitConfirmation':[label('Title','= "Submit job plan for review"',20),label('Confirmation','= "Submission creates a new review case. The previous approved plan remains active."',100),button('Confirm','Confirm submission','=Notify("Connect the authorised SubmitRevision flow before use",NotificationType.Warning)',200),button('Cancel','Return to draft','=Navigate(PlanEditor)',255)],
 'ReviewCase':[label('Title','= "Review proposed revision"',20),label('Warning','= "Verify industrial rules, consultation and delegated authority before decision"',80),button('Compare','Compare versions','=Navigate(VersionComparison)',160),button('Approve','Approve (delegated)','=Notify("Awaiting server-enforced approval flow binding",NotificationType.Warning)',230),button('Return','Return for changes','=Notify("Awaiting server-enforced decision flow binding",NotificationType.Warning)',290),button('Back','Queue','=Navigate(ApproverDashboard)',365)],
 'VersionHistory':[label('Title','= "Job-plan version history"',20),gallery('History',"=Filter(JP_PlanVersions, PlanKey = varSelectedPlanKey)",90),button('Compare','Compare selected','=Navigate(VersionComparison)',400),button('Back','My plans','=Navigate(PractitionerDashboard)',460)],
 'VersionComparison':[label('Title','= "Compare approved and proposed job plans"',20),label('DiffPlaceholder','= "Differences are calculated by the qualified domain comparison service."',90),button('Back','History','=Navigate(VersionHistory)',200)],
 'OperatorDashboard':[label('Title','= "Operational assurance"',20),gallery('OpenOperations',"=Filter(JP_Operations, Status = \"Prepared\")",90),button('Back','Home','=Navigate(Home)',410)]
}
# The only authority for access is the server/SharePoint ACL. These flags are
# presentation hints from a future trusted role-projection flow and default closed.
screens['Home'][1]['MyPlans']['Properties']['Visible'] = '=Coalesce(varCanViewOwnPlans,false)'
screens['Home'][2]['MyApprovals']['Properties']['Visible'] = '=Coalesce(varCanApprove,false)'
screens['Home'][3]['Administration']['Properties']['Visible'] = '=Coalesce(varCanOperate,false)'
screens['ApproverDashboard'][1]['AssignedReviews']['Properties']['Visible'] = '=Coalesce(varCanApprove,false)'
screens['OperatorDashboard'][1]['OpenOperations']['Properties']['Visible'] = '=Coalesce(varCanOperate,false)'
# A screen can be reached by navigation and must not become an access-control boundary.
# The SharePoint lists and all privileged flows must separately deny unauthorised access.

for name,children in screens.items():
    obj={'Screens':{name:{'Children':children}}}
    (SRC/f'{name}.pa.yaml').write_text('# REVIEWABLE POWER APPS SOURCE SPECIFICATION; not Power Apps Studio validated\n'+yaml.safe_dump(obj,sort_keys=False,allow_unicode=True),encoding='utf8')
(SRC/'App.pa.yaml').write_text('App:\n  Properties:\n    StartScreen: =Home\n',encoding='utf8')

# Workflow contracts are valid Workflow Definition Language JSON. Connector bindings,
# workflow triggers and expressions must be configured by solution import/maker.
def flow(name,kind,steps):
    if kind=='recurrence':trigger={'Scheduled':{'type':'Recurrence','recurrence':{'frequency':'Day','interval':1,'timeZone':'E. Australia Standard Time','startTime':'2027-01-01T00:00:00'}}}
    else:trigger={'PowerAppsV2':{'type':'Request','kind':'PowerAppV2','inputs':{'schema':{'type':'object','properties':{'operationKey':{'type':'string'},'planKey':{'type':'string'}}}}}}
    actions={}
    previous=[]
    for n,description in enumerate(steps,1):
        key=f'Step_{n:02}'
        actions[key]={'type':'Compose','inputs':{'design_step':description,'must_bind_before_enable':True},'runAfter':{previous[-1]:['Succeeded']} if previous else {}}
        previous.append(key)
    return {'$schema':'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#',
            'contentVersion':'0.1.0.0','parameters':{},'triggers':trigger,'actions':actions,'outputs':{},
            '_implementationStatus':'binding-required/disabled; placeholder compose actions are NOT operational'}
flows={
'01-submit-revision':('app',['Resolve caller identity from trusted connection, not submitted UPN','Check draft ownership and version/ETag','Validate cycle hours, CST, applicability and source policies','Create operation receipt and immutable candidate','CAS plan head; create restricted review case; finalise receipt']),
'02-review-route':('app',['Read case and version hash','Resolve clinical director, HR/IR and delegate with effective-dated role grants','Enforce segregation of duties and service boundaries','CAS case transition, append immutable decision event','Queue next stage or terminal outcome']),
'03-review-due-sweep':('recurrence',['Read approved effective-dated review policy','Find due plans and matching policy edition','Create unique review obligation key','Reconcile existing case and prevent duplicate scheduling','Create limited-data alert receipt']),
'04-notify-digest':('recurrence',['Read unnotified assigned cases and obligations','Check recipient is authorised and still effective','Deduplicate notification operations by recipient+stage+period','Send minimal-data digest using approved standard connector','Persist delivered or retry receipt']),
'05-activate-approved':('recurrence',['Find approved candidates at effective date','Check delegated decision chain, current generation and record hash','Conditionally CAS active approved plan pointer','Retain prior version and update projections','Reconcile interrupted operation']),
'06-reconcile-operations':('recurrence',['Read prepared operations and unmatched artifacts','Compare head last_operation and commit generation','Finalise committed receipts or quarantine ambiguous operations','Detect orphan tasks/expired delegations/failed exports','Expose operator exception summary without personal content']),
'07-no-change-review':('app',['Resolve reviewer and due obligation','Check current approved version and review authority','Record explicit no-change human attestation','Close obligation idempotently without manufacturing new version','Create next policy-derived due date']),
'08-export-version':('app',['Authorise actor for requested historical version','Read immutable version and approved decision trail','Render approved corporate document template in restricted library','Verify digest and link scope','Record export and audit event']),
'09-cst-exception':('app',['Authorise officer or service leader','Record CST displacement as separate event','Check mandatory recovery reason and date','Create recovery reminder and service exception','Reconcile recovery ledger without double count']),
'10-assignment-update':('app',['Read verified position and employment change','Check effective date/service and approved data source','Invalidate stale approver tasks and recompute future routing','Do not modify active plan without approved revision','Audit assignment-change consequence'])
}
for name,(kind,steps) in flows.items():
    (FLOWS/(name+'.workflow.json')).write_text(json.dumps(flow(name,kind,steps),indent=2)+'\n')
(FLOWS/'catalogue.json').write_text(json.dumps({'state':'disabled-source-contracts-only','flows':[{'name':k,'trigger':v[0],'required_steps':v[1]} for k,v in flows.items()]},indent=2)+'\n')
print('generated',len(screens),'screen specifications and',len(flows),'WDL placeholders')
