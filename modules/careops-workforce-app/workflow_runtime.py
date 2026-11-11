"""Offline transactional reference for job-plan versions, reviews and dual-role queues.

All identities and dates are synthetic caller inputs. This module never bypasses
SharePoint permissions and is NOT a Power Automate runtime or legal approval engine.
"""
from __future__ import annotations

from calendar import monthrange
from contextlib import contextmanager
from datetime import date
from hashlib import sha256
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sqlite3
from uuid import uuid4


class AccessDenied(PermissionError): pass
class InvalidState(ValueError): pass
class StaleState(InvalidState): pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def add_months(start, months):
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def validate_submission(content):
    """Reference geometry validation; does not certify authority of rule_ref."""
    if not isinstance(content, dict) or not isinstance(content.get('sessions'), list):
        raise InvalidState('plan must have a session list')
    weeks=content.get('cycle_weeks')
    if not isinstance(weeks,int) or isinstance(weeks,bool) or not 1<=weeks<=26:
        raise InvalidState('cycle length out of bounds')
    if not isinstance(content.get('rule_ref'),str) or not content['rule_ref'].strip():
        raise InvalidState('source rule reference required')
    try:
        contracted=Decimal(str(content['contracted_fortnight_hours']))
        planned=Decimal(str(content['planned_hours']))
        cst=Decimal(str(content['cst_hours']))
        rate=Decimal(str(content['minimum_cst_fraction']))
    except (InvalidOperation, KeyError, ValueError, TypeError) as e:
        raise InvalidState('invalid hour or entitlement values') from e
    if (not all(v.is_finite() for v in (contracted,planned,cst,rate))
       or contracted<=0 or not 0<=cst<=planned or not 0<=rate<=1
       or planned!=contracted*Decimal(weeks)/2 or cst<planned*rate):
        raise InvalidState('unbalanced cycle or inadequate protected time')
    # A real workflow must separately validate applicable instrument and
    # source-authorised CST classification; caller-supplied rule values are
    # deliberately NOT an authorisation check.
    return True

STAGES = ('consultation', 'clinical_review', 'industrial_review', 'delegated_approval')
STAGE_ROLES = ('clinical_director', 'clinical_director', 'medical_workforce', 'approver')


class WorkforceRuntime:
    """SQLite serialisable local simulator; live SharePoint needs saga/ETag adapter."""
    def __init__(self, path):
        self.path = str(Path(path))
        with self.tx() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY, owner TEXT NOT NULL, service TEXT NOT NULL,
                active TEXT, generation INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS grants (
                subject TEXT NOT NULL, role TEXT NOT NULL, service TEXT NOT NULL,
                valid_from TEXT NOT NULL, valid_to TEXT NOT NULL,
                PRIMARY KEY (subject,role,service,valid_from));
            CREATE TABLE IF NOT EXISTS versions (
                id TEXT PRIMARY KEY, plan TEXT NOT NULL, base_version TEXT,
                content TEXT NOT NULL, digest TEXT NOT NULL, status TEXT NOT NULL,
                effective_from TEXT, approved_by TEXT, submitted_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY, plan TEXT NOT NULL, version TEXT NOT NULL,
                status TEXT NOT NULL, stage INTEGER NOT NULL DEFAULT 0,
                generation INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY, case_id TEXT NOT NULL, version TEXT NOT NULL,
                stage TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL,
                decided_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS operations (
                id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS review_rules (
                id TEXT NOT NULL, service TEXT NOT NULL, months INTEGER NOT NULL,
                from_date TEXT NOT NULL, to_date TEXT NOT NULL, edition INTEGER NOT NULL,
                PRIMARY KEY(id,service,edition));
            CREATE TABLE IF NOT EXISTS obligations (
                id TEXT PRIMARY KEY, plan TEXT NOT NULL, rule_id TEXT NOT NULL,
                rule_edition INTEGER NOT NULL, due_date TEXT NOT NULL,
                status TEXT NOT NULL, decided_by TEXT,
                UNIQUE(plan,rule_id,rule_edition,due_date));
            CREATE INDEX IF NOT EXISTS idx_case_plan ON cases(plan,status);
            CREATE INDEX IF NOT EXISTS idx_plan_owner ON plans(owner,service);
            CREATE INDEX IF NOT EXISTS idx_obligation_due ON obligations(due_date,status);
            ''')

    @contextmanager
    def tx(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA busy_timeout=10000')
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _permission(db, subject, role, service, today):
        if not db.execute('''SELECT 1 FROM grants WHERE subject=? AND role=?
               AND service=? AND valid_from<=? AND valid_to>?''',
               (subject,role,service,today,today)).fetchone():
            raise AccessDenied('actor lacks effective service-scoped role')

    @staticmethod
    def _plan(db, plan):
        p = db.execute('SELECT * FROM plans WHERE id=?', (plan,)).fetchone()
        if p is None: raise InvalidState('unknown plan')
        return dict(p)

    @staticmethod
    def _replay(db, key, fingerprint):
        existing = db.execute('SELECT * FROM operations WHERE id=?',(key,)).fetchone()
        if existing is None:return None
        if existing['fingerprint'] != fingerprint:raise InvalidState('operation key rebound')
        return json.loads(existing['result'])

    @staticmethod
    def _record(db, key, fingerprint, result):
        db.execute('INSERT INTO operations VALUES(?,?,?)', (key,fingerprint,canonical(result)))
        return result

    def add_grant(self, subject, role, service, start, end):
        if role not in (*STAGE_ROLES,'practitioner') or date.fromisoformat(start)>=date.fromisoformat(end):
            raise InvalidState('invalid role interval')
        with self.tx() as db:
            db.execute('INSERT OR IGNORE INTO grants VALUES(?,?,?,?,?)', (subject,role,service,start,end))

    def create_plan(self, plan, owner, service):
        if not all((plan,owner,service)):raise InvalidState('missing plan identity')
        with self.tx() as db:
            db.execute('INSERT INTO plans(id,owner,service) VALUES(?,?,?)',(plan,owner,service))

    def submit(self,plan,actor,content,operation,today):
        date.fromisoformat(today)
        validate_submission(content)
        fp=digest(['submit',plan,actor,content,today])
        with self.tx() as db:
            past=self._replay(db,operation,fp)
            if past is not None:return past
            p=self._plan(db,plan)
            self._permission(db,actor,'practitioner',p['service'],today)
            if p['owner']!=actor:raise AccessDenied('not owner')
            if db.execute("SELECT 1 FROM cases WHERE plan=? AND status='pending'",(plan,)).fetchone():
                raise InvalidState('submitted revision already in review')
            version='v-'+uuid4().hex
            case='c-'+uuid4().hex
            payload=canonical(content)
            db.execute('''INSERT INTO versions
                (id,plan,base_version,content,digest,status,submitted_at)
                VALUES(?,?,?,?,?,?,?)''',
                (version,plan,p['active'],payload,sha256(payload.encode()).hexdigest(),'submitted',today))
            db.execute("INSERT INTO cases(id,plan,version,status) VALUES(?,?,?,'pending')",(case,plan,version))
            result={'case_id':case,'version_id':version,'status':'submitted','version_digest':sha256(payload.encode()).hexdigest()}
            return self._record(db,operation,fp,result)

    def decide(self,case,actor,action,operation,today,effective_date=None,expected_generation=None):
        date.fromisoformat(today)
        if action not in ('approve','return','reject'):raise InvalidState('invalid decision action')
        if effective_date is not None:date.fromisoformat(effective_date)
        fp=digest(['decision',case,actor,action,today,effective_date,expected_generation])
        with self.tx() as db:
            past=self._replay(db,operation,fp)
            if past is not None:return past
            c=db.execute('SELECT * FROM cases WHERE id=?',(case,)).fetchone()
            if c is None:raise InvalidState('unknown case')
            c=dict(c)
            if c['status']!='pending':raise InvalidState('case is terminal')
            if expected_generation is not None and c['generation']!=expected_generation:
                raise StaleState('case revision stale')
            p=self._plan(db,c['plan'])
            stage=c['stage']
            self._permission(db,actor,STAGE_ROLES[stage],p['service'],today)
            if actor==p['owner']:raise AccessDenied('self approval prohibited')
            if action=='approve' and stage==len(STAGES)-1:
                if effective_date is None or effective_date<today:raise InvalidState('invalid effective date')
                if db.execute("SELECT 1 FROM versions WHERE plan=? AND status='approved_pending'",(p['id'],)).fetchone():
                    raise InvalidState('future activation already awaiting')
                db.execute("UPDATE versions SET status='approved_pending',effective_from=?,approved_by=? WHERE id=?",
                           (effective_date,actor,c['version']))
                status='approved'
            elif action=='approve':
                if effective_date is not None:raise InvalidState('effective date allowed only at final approval')
                status='pending'
            else:
                if effective_date is not None:raise InvalidState('no date on return/reject')
                status={'return':'returned','reject':'rejected'}[action]
                db.execute('UPDATE versions SET status=? WHERE id=?',(status,c['version']))
            db.execute('UPDATE cases SET status=?,stage=?,generation=generation+1 WHERE id=?',
                       (status,stage+int(action=='approve' and stage<len(STAGES)-1),case))
            db.execute('INSERT INTO decisions VALUES(?,?,?,?,?,?,?)',
                       (operation,case,c['version'],STAGES[stage],actor,action,today))
            return self._record(db,operation,fp,{'case_id':case,'status':status,'next_stage':
               (STAGES[stage+1] if action=='approve' and stage+1<len(STAGES) else None)})

    def activate_due(self, today):
        date.fromisoformat(today)
        with self.tx() as db:
            rows=db.execute("SELECT id,plan FROM versions WHERE status='approved_pending' AND effective_from<=? ORDER BY effective_from,id",(today,)).fetchall()
            for v in rows:
                db.execute("UPDATE versions SET status='superseded' WHERE plan=? AND status='active'",(v['plan'],))
                db.execute("UPDATE versions SET status='active' WHERE id=?",(v['id'],))
                db.execute('UPDATE plans SET active=?,generation=generation+1 WHERE id=?',(v['id'],v['plan']))
            return len(rows)

    def history(self,plan,actor,today):
        with self.tx() as db:
            p=self._plan(db,plan)
            if p['owner']==actor:self._permission(db,actor,'practitioner',p['service'],today)
            else:
                if not any(db.execute('''SELECT 1 FROM grants WHERE subject=? AND role=? AND service=? AND valid_from<=? AND valid_to>?''',
                        (actor,role,p['service'],today,today)).fetchone() for role in STAGE_ROLES):
                    raise AccessDenied('no delegated history access')
            return [dict(v) for v in db.execute('''SELECT id AS version_id,status,effective_from,approved_by,submitted_at,digest
                FROM versions WHERE plan=? ORDER BY submitted_at,id''',(plan,)).fetchall()]

    def get_case(self,case,actor,today):
        with self.tx() as db:
            c=db.execute('SELECT * FROM cases WHERE id=?',(case,)).fetchone()
            if c is None:raise InvalidState('unknown case')
            p=self._plan(db,c['plan'])
            if actor==p['owner']:self._permission(db,actor,'practitioner',p['service'],today)
            else:
                self._permission(db,actor,STAGE_ROLES[min(c['stage'],3)],p['service'],today)
            return dict(c)

    def add_review_rule(self,rule,service,months,start,end,edition):
        if not rule or not service or edition<1 or months<1 or months>120 or start>=end:raise InvalidState('bad review rule')
        date.fromisoformat(start);date.fromisoformat(end)
        with self.tx() as db:
            for other in db.execute('SELECT * FROM review_rules WHERE id=? AND service=?',(rule,service)).fetchall():
                if max(start,other['from_date'])<min(end,other['to_date']):raise InvalidState('overlapping authority rule')
            db.execute('INSERT INTO review_rules VALUES(?,?,?,?,?,?)',(rule,service,months,start,end,edition))

    def sweep_reviews(self,today):
        today_date=date.fromisoformat(today)
        made=0
        with self.tx() as db:
            for rule in db.execute('SELECT * FROM review_rules').fetchall():
                anchor=date.fromisoformat(rule['from_date'])
                effective_end=date.fromisoformat(rule['to_date'])
                for p in db.execute('SELECT id FROM plans WHERE service=?',(rule['service'],)).fetchall():
                    n=0
                    while n<240:
                        period_start=add_months(anchor,n*rule['months'])
                        due=add_months(anchor,(n+1)*rule['months'])
                        if period_start>=effective_end or due>today_date:break
                        key=digest(['review',p['id'],rule['id'],rule['edition'],due.isoformat()])
                        count=db.execute('INSERT OR IGNORE INTO obligations VALUES(?,?,?,?,?, ?, NULL)',
                           (key,p['id'],rule['id'],rule['edition'],due.isoformat(),'open')).rowcount
                        made+=count
                        n+=1
                    if n==240:raise InvalidState('review sweep horizon exceeded')
        return made

    def attest_no_change(self,plan,actor,rule,due,operation,today):
        fp=digest(['attest',plan,actor,rule,due,today])
        with self.tx() as db:
            past=self._replay(db,operation,fp)
            if past is not None:return past
            p=self._plan(db,plan)
            self._permission(db,actor,'approver',p['service'],today)
            if actor==p['owner']:raise AccessDenied('self review')
            row=db.execute("SELECT * FROM obligations WHERE plan=? AND rule_id=? AND due_date=? AND status='open'",
                           (plan,rule,due)).fetchone()
            if row is None:raise InvalidState('no open due obligation')
            db.execute("UPDATE obligations SET status='complete',decided_by=? WHERE id=?",(actor,row['id']))
            return self._record(db,operation,fp,{'obligation_id':row['id'],'status':'complete'})

    def available_workspaces(self,actor,today):
        with self.tx() as db:
            roles={r['role'] for r in db.execute('SELECT role FROM grants WHERE subject=? AND valid_from<=? AND valid_to>?',
                                                 (actor,today,today)).fetchall()}
            result=[]
            if roles.intersection(set(STAGE_ROLES)):result.append('approver')
            if 'practitioner' in roles:result.append('practitioner')
            return result

    def practitioner_dashboard(self,actor,today):
        with self.tx() as db:
            own=[]
            for p in db.execute('SELECT * FROM plans WHERE owner=?',(actor,)).fetchall():
                self._permission(db,actor,'practitioner',p['service'],today)
                pending=db.execute("SELECT COUNT(*) FROM cases WHERE plan=? AND status='pending'",(p['id'],)).fetchone()[0]
                own.append({'plan_id':p['id'],'active_version':p['active'],'pending_cases':pending})
            return {'plans':own,'workspace':'practitioner'}

    def approver_dashboard(self,actor,today):
        with self.tx() as db:
            eligible={r['service'] for r in db.execute('''SELECT service FROM grants WHERE subject=? AND role IN
              ('clinical_director','medical_workforce','approver') AND valid_from<=? AND valid_to>?''',(actor,today,today)).fetchall()}
            if not eligible:raise AccessDenied('no approver workspace')
            cases=[];obligations=[]
            for c in db.execute("SELECT c.*,p.owner,p.service FROM cases c JOIN plans p ON p.id=c.plan WHERE c.status='pending'").fetchall():
                if c['service'] in eligible and c['owner']!=actor:
                    role=STAGE_ROLES[c['stage']]
                    try:self._permission(db,actor,role,c['service'],today)
                    except AccessDenied:continue
                    cases.append({'case_id':c['id'],'plan_id':c['plan'],'stage':STAGES[c['stage']]})
            for o in db.execute("SELECT o.*,p.owner,p.service FROM obligations o JOIN plans p ON p.id=o.plan WHERE o.status='open'").fetchall():
                if o['service'] in eligible and o['owner']!=actor:
                    obligations.append(dict(o))
            return {'workspace':'approver','cases':cases,'obligations':obligations}
