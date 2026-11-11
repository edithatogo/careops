# SPDX-License-Identifier: Apache-2.0
"""Crash-recoverable SharePoint CAS protocol for medical job-plan revisions.

This source is a deployable adapter contract, not a hosted service or a claim
that SharePoint supports transactions across lists. Only one list-item compare-
and-swap is the linearization point; unique staged artifacts and operation
receipts are projections recovered after interruption. Caller identity must be
resolved by an authenticated, least-privileged Power Automate boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from datetime import date
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import quote


class Conflict(RuntimeError): pass
class Forbidden(RuntimeError): pass
class InvalidTransition(RuntimeError): pass
class AmbiguousOperation(RuntimeError): pass
class InjectedCrash(RuntimeError): pass


def canonical_json(value: Any) -> str:
    if not isinstance(value, dict):
        raise ValueError('expected JSON object')
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False, ensure_ascii=False)
    if json.loads(raw) != value:
        raise ValueError('non round-trip-safe JSON')
    return raw


def canonical_digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()


@dataclass(frozen=True)
class Principal:
    """Authoritative actor/roles supplied by validated server auth, never the app body."""
    subject: str
    scopes: frozenset[str]


class Store(Protocol):
    def get(self, list_name: str, key: str) -> tuple[dict[str, Any] | None, str | None]: ...
    def create_unique(self, list_name: str, key: str, value: dict[str, Any]) -> bool: ...
    def cas(self, list_name: str, key: str, etag: str, value: dict[str, Any]) -> None: ...


class SqliteSharePointSimulator:
    """Crash-persistent local SharePoint semantics: unique keys and conditional ETags.

    Deliberately a simulator, NOT a replacement for SharePoint permissions.
    """
    def __init__(self, path: str):
        self.path = str(Path(path))
        with self._conn() as db:
            db.execute('CREATE TABLE IF NOT EXISTS items ('
                       'list_name TEXT NOT NULL, key TEXT NOT NULL, payload TEXT NOT NULL, '
                       'etag INTEGER NOT NULL, PRIMARY KEY(list_name,key))')

    @contextmanager
    def _conn(self):
        db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        try:
            db.execute('PRAGMA busy_timeout=15000')
            yield db
        finally:
            db.close()

    def get(self, list_name: str, key: str):
        with self._conn() as db:
            row = db.execute('SELECT payload, etag FROM items WHERE list_name=? AND key=?', (list_name,key)).fetchone()
        return (json.loads(row[0]), str(row[1])) if row else (None, None)

    def create_unique(self, list_name: str, key: str, value: dict[str, Any]) -> bool:
        with self._conn() as db:
            try:
                db.execute('INSERT INTO items VALUES(?,?,?,1)',(list_name,key,canonical_json(value)))
                return True
            except sqlite3.IntegrityError:
                return False

    def cas(self, list_name: str, key: str, etag: str, value: dict[str, Any]):
        if not etag or etag == '*': raise Conflict('exact If-Match ETag required')
        with self._conn() as db:
            result = db.execute('UPDATE items SET payload=?, etag=etag+1 '
                                'WHERE list_name=? AND key=? AND etag=?',
                                (canonical_json(value),list_name,key,etag))
            if result.rowcount != 1: raise Conflict('SharePoint 412 stale ETag')

    def list_artifacts(self, plan_id: str) -> list[dict[str, Any]]:
        with self._conn() as db:
            rows=db.execute("SELECT payload FROM items WHERE list_name='artifacts'").fetchall()
        return [json.loads(x[0]) for x in rows if json.loads(x[0]).get('plan_id')==plan_id]


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: dict[str, Any] | None = None
    headers: Mapping[str,str] | None = None


class SharePointRestStore:
    """Live REST mapping for the standard 'Send an HTTP request to SharePoint' action.

    Must be called from server-owned flows with approved connection identity;
    no bearer token or credentials are held in the library. Provision three
    indexed unique Key columns, Payload multiline text, and list access ACLs.
    """
    def __init__(self, send: Callable[[str, str, Mapping[str,str], dict[str,Any] | None], HttpResponse],
                 lists: Mapping[str,str]):
        self.send=send
        self.lists={k:lists[k] for k in ('heads','operations','artifacts','obligations')}
        if any(not name or not name.replace("-", "").replace("_", "").isalnum() for name in self.lists.values()):
            raise ValueError("invalid SharePoint list name")

    def _query(self, name: str, key: str) -> tuple[dict[str,Any] | None,str | None,int | None]:
        escaped=key.replace("'","''")
        endpoint=f"_api/web/lists/getbytitle('{self.lists[name]}')/items?$filter="+quote(f"Key eq '{escaped}'",safe="()'$= ")
        response=self.send('GET',endpoint,{'Accept':'application/json;odata=nometadata'},None)
        if response.status >= 400: raise RuntimeError(f'SharePoint query failed {response.status}')
        items=(response.body or {}).get('value',[])
        if len(items)>1: raise RuntimeError('uniqueness violated')
        if not items: return None,None,None
        item=items[0]
        return json.loads(item['Payload']), item.get('@odata.etag') or item.get('odata.etag'), int(item['Id'])

    def get(self, name: str, key: str):
        value,etag,_=self._query(name,key)
        return value,etag

    def create_unique(self,name: str,key: str,value: dict[str,Any]):
        endpoint=f"_api/web/lists/getbytitle('{self.lists[name]}')/items"
        r=self.send('POST',endpoint,{'Accept':'application/json;odata=nometadata','Content-Type':'application/json;odata=nometadata'},
                    {'Key':key,'Title':key[:255],'Payload':canonical_json(value)})
        if r.status in (200,201,204): return True
        # SharePoint unique-index conflict often surfaces as 400, not just 409.
        # Only classify it as a duplicate after verifying that exact Key exists.
        if r.status in (400,409,412):
            found,_,_=self._query(name,key)
            if found is not None:return False
        raise RuntimeError(f'SharePoint create failed {r.status}')

    def cas(self,name:str,key:str,etag:str,value:dict[str,Any]):
        if not etag or etag=='*':raise Conflict('exact If-Match ETag required')
        _,current,item_id=self._query(name,key)
        if item_id is None:raise Conflict('missing target')
        if current!=etag:raise Conflict('stale ETag')
        endpoint=f"_api/web/lists/getbytitle('{self.lists[name]}')/items({item_id})"
        r=self.send('POST',endpoint,{'Accept':'application/json;odata=nometadata',
          'Content-Type':'application/json;odata=nometadata','X-HTTP-Method':'MERGE','IF-MATCH':etag},
          {'Payload':canonical_json(value)})
        if r.status in (409,412):raise Conflict('SharePoint 412 stale ETag')
        if r.status not in (200,204):raise RuntimeError(f'SharePoint conditional update failed {r.status}')


class Adapter:
    def __init__(self, store: Store):
        self.store=store

    def bootstrap(self, plan_id: str, owner: str, service: str):
        if not all((plan_id, owner, service)):raise ValueError('missing plan identity')
        state={'plan_id':plan_id,'owner':owner,'service':service,'generation':0,
               'current':None,'pending':None,'scheduled':None,'history':[],
               'last_operation':None}
        if not self.store.create_unique('heads',plan_id,state):raise Conflict('plan already exists')

    @staticmethod
    def _authorise(principal:Principal, state:dict,role:str):
        if not principal.subject or f'{role}:{state["service"]}' not in principal.scopes:
            raise Forbidden('role/service not authorised')
        if role=='practitioner' and principal.subject!=state['owner']:
            raise Forbidden('not plan owner')
        if role=='approver' and principal.subject==state['owner']:
            raise Forbidden('self-approval')

    def _read_head(self,plan_id:str):
        state,etag=self.store.get('heads',plan_id)
        if state is None or etag is None:raise ValueError('unknown plan')
        return state,etag

    def read(self,plan_id:str,principal:Principal):
        state,_=self._read_head(plan_id)
        if principal.subject==state['owner']:
            self._authorise(principal,state,'practitioner')
        else:self._authorise(principal,state,'approver')
        return state

    def history(self,plan_id:str,principal:Principal):
        return list(self.read(plan_id,principal)['history'])

    def operation(self,key:str):
        o,_=self.store.get('operations',key)
        return o

    def _settle_previous(self,state:dict):
        last=state.get('last_operation')
        if not last:return
        receipt,etag=self.store.get('operations',last)
        if receipt is None or etag is None:raise InvalidTransition('head references missing operation')
        if receipt['status']=='prepared':
            updated={**receipt,'status':'committed','result':state}
            try:self.store.cas('operations',last,etag,updated)
            except Conflict:
                check,_=self.store.get('operations',last)
                if check is None or check.get('status')!='committed':raise

    def _transaction(self,plan_id:str,principal:Principal,role:str,op:str,
                     request:dict[str,Any],expected_generation:int,
                     mutation:Callable[[dict[str,Any]],dict[str,Any]],
                     artifact:dict[str,Any] | None=None,crash_after_cas:bool=False):
        if not op or not principal.subject:raise ValueError('operation ID and server-resolved identity required')
        fingerprint=canonical_digest({'operation':op,'principal':principal.subject,
                                      'plan_id':plan_id,'request':request,'expected':expected_generation})
        state,etag=self._read_head(plan_id)
        self._authorise(principal,state,role)
        receipt,receipt_etag=self.store.get('operations',op)
        if receipt is not None:
            if receipt['digest']!=fingerprint:raise AmbiguousOperation('operation ID reused for different request')
            if receipt['status']=='committed':return receipt['result']
            # A crash between HEAD CAS and receipt finalisation.
            if state.get('last_operation')==op:
                self._settle_previous(state)
                return state
        else:
            receipt={'key':op,'plan_id':plan_id,'digest':fingerprint,'status':'prepared'}
            if not self.store.create_unique('operations',op,receipt):
                return self._transaction(plan_id,principal,role,op,request,expected_generation,
                                         mutation,artifact,crash_after_cas)
        self._settle_previous(state)
        if state['generation']!=expected_generation:raise Conflict('stale plan generation')
        proposed=mutation(dict(state))
        proposed['generation']=expected_generation+1
        proposed['last_operation']=op
        # Staged immutable artifact is not authoritative unless referenced
        # by the CAS-committed head. Orphans are explicitly excluded from history.
        if artifact is not None:
            item={**artifact,'plan_id':plan_id,'transaction_key':op}
            if not self.store.create_unique('artifacts',op,item):
                old,_=self.store.get('artifacts',op)
                if old!=item:raise AmbiguousOperation('artifact mismatch on retry')
        self.store.cas('heads',plan_id,etag,proposed)
        if crash_after_cas:raise InjectedCrash('fault injected after CAS, before receipt finalisation')
        self._settle_previous(proposed)
        return proposed

    def submit(self,plan_id:str,principal:Principal,version_id:str,content:dict[str,Any],
               op:str,expected_generation:int,crash_after_cas:bool=False):
        digest=canonical_digest(content)
        def mutate(s):
            if s['pending'] is not None or s['scheduled'] is not None:
                raise InvalidTransition('existing candidate in progress')
            if version_id in s['history'] or version_id==s['current']:
                raise InvalidTransition('version already exists')
            s['pending']={'version_id':version_id,'digest':digest,'submitted_by':principal.subject}
            return s
        return self._transaction(plan_id,principal,'practitioner',op,
                                 {'command':'submit','version_id':version_id,'digest':digest},
                                 expected_generation,mutate,
                                 {'type':'version','version_id':version_id,'digest':digest,'content':content},
                                 crash_after_cas)

    def decide(self,plan_id:str,principal:Principal,action:str,op:str,expected_generation:int,
               effective_date:str | None=None):
        if action not in ('approve','reject'):raise InvalidTransition('invalid decision')
        def mutate(s):
            pending=s['pending']
            if pending is None:raise InvalidTransition('no candidate')
            if action=='approve':
                if not effective_date or date.fromisoformat(effective_date)<date.today():
                    raise InvalidTransition('effective date must be today or later')
                s['scheduled']={'version_id':pending['version_id'],'effective_date':effective_date,
                                'approved_by':principal.subject,'decision_operation':op}
                s['history']=s['history']+[pending['version_id']]
            else:
                if effective_date is not None:raise InvalidTransition('reject cannot set effective date')
            s['pending']=None
            return s
        return self._transaction(plan_id,principal,'approver',op,
              {'command':'decision','action':action,'effective_date':effective_date},
              expected_generation,mutate,
              {'type':'decision','action':action,'effective_date':effective_date,'actor':principal.subject})

    def activate(self,plan_id:str,principal:Principal,op:str,expected_generation:int,
                 as_of:str):
        def mutate(s):
            scheduled=s['scheduled']
            if scheduled is None:raise InvalidTransition('nothing scheduled')
            if date.fromisoformat(as_of)<date.fromisoformat(scheduled['effective_date']):
                raise InvalidTransition('future activation not yet effective')
            s['current']=scheduled['version_id']
            s['scheduled']=None
            return s
        return self._transaction(plan_id,principal,'approver',op,
             {'command':'activate','as_of':as_of},expected_generation,mutate)

    def review_obligation(self,plan_id:str,principal:Principal,rule_id:str,rule_version:int,due:str):
        state=self.read(plan_id,principal)
        self._authorise(principal,state,'approver')
        date.fromisoformat(due)
        if not rule_id or rule_version<1:raise ValueError('invalid effective policy reference')
        key=canonical_digest({'plan':plan_id,'rule':rule_id,'edition':rule_version,'due':due})
        data={'key':key,'plan_id':plan_id,'rule_id':rule_id,'rule_version':rule_version,
              'due':due,'status':'open'}
        if not self.store.create_unique('obligations',key,data):
            saved,_=self.store.get('obligations',key)
            if saved!=data:raise AmbiguousOperation('obligation key collision')
        return data
