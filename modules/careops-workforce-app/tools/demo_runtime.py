"""Entirely synthetic clinician/approver lifecycle demonstration, offline only."""
import json
import tempfile
from pathlib import Path
from workflow_runtime import WorkforceRuntime


def demonstrate():
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'synthetic.sqlite3'
        app=WorkforceRuntime(db)
        for who,role in [('synthetic-clinician','practitioner'),('synthetic-director','clinical_director'),
                         ('synthetic-HR','medical_workforce'),('synthetic-delegate','approver')]:
            app.add_grant(who,role,'FICTIONAL_SERVICE','2026-01-01','2030-01-01')
        app.create_plan('synthetic-plan','synthetic-clinician','FICTIONAL_SERVICE')
        app.add_review_rule('FICTIONAL_ANNUAL','FICTIONAL_SERVICE',12,'2026-01-01','2030-01-01',1)
        draft={'cycle_weeks':2,'contracted_fortnight_hours':'80','planned_hours':'80',
               'cst_hours':'10','minimum_cst_fraction':'0.10','rule_ref':'FICTIONAL_RULE_V1','sessions':[]}
        submitted=app.submit('synthetic-plan','synthetic-clinician',draft,'SYNTHETIC_SUBMIT','2026-11-11')
        case=submitted['case_id']
        for n,who in enumerate(['synthetic-director','synthetic-director','synthetic-HR','synthetic-delegate']):
            app.decide(case,who,'approve',f'SYNTHETIC_APPROVAL_{n}','2026-11-11',
                       effective_date='2026-12-01' if n==3 else None)
        assert app.activate_due('2026-11-30')==0
        assert app.activate_due('2026-12-01')==1
        assert app.activate_due('2026-12-01')==0
        assert app.sweep_reviews('2027-01-02')==1
        app.attest_no_change('synthetic-plan','synthetic-delegate','FICTIONAL_ANNUAL',
                             '2027-01-01','SYNTHETIC_ATTEST','2027-01-02')
        return {'simulation':'PASS','no_real_staff_data':True,
                'history_count':len(app.history('synthetic-plan','synthetic-clinician','2027-01-02')),
                'active_plan':app.practitioner_dashboard('synthetic-clinician','2027-01-02')['plans'][0]['active_version'] is not None,
                'clinician_workspaces':app.available_workspaces('synthetic-clinician','2027-01-02'),
                'approver_workspaces':app.available_workspaces('synthetic-delegate','2027-01-02'),
                'status':'local-only; no Microsoft/CHHHS connections'}

if __name__=='__main__':
    print(json.dumps(demonstrate(),indent=2))
