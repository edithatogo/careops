"""Consume existing privately accepted JSON captures into typed RIMS products.

No source fetching, Graph access, Power Automate calls, approvals or sends.
The source custodian supplies an independently verified receipt and rights.
All result products are PRIVATE; only redacted aggregate counts may be logged.
"""
from __future__ import annotations
import base64
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def _load(name):
    spec=spec_from_file_location(name,ROOT/(name+'.py'))
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
occ=_load('rims_json_occurrences')
product=_load('rims_source_products')

MAX_RECORDS=2000
MAX_BATCH_BYTES=64_000_000

class BatchError(ValueError):pass

def project_batch(batch,receipt,mapping,catalogue,*,verify_receipt=None,verify_mapping=None):
    if not all(isinstance(v,dict) for v in (batch,receipt,mapping,catalogue)):
        raise BatchError('private batch, receipts, mapping and catalogue required')
    if (batch.get('schema')!='careops-rims.retained-json-batch/1' or
        receipt.get('schema')!='careops-rims.retained-source-receipt/1' or
        catalogue.get('schema')!='careops-rims.existing-source-adoption/1'):
        raise BatchError('unqualified contract')
    source=batch.get('source_id')
    allowed={v.get('source') for v in catalogue.get('sources',[]) if isinstance(v,dict)}
    if not isinstance(source,str) or source not in allowed or source != receipt.get('source_id') or source != mapping.get('source_id'):
        raise BatchError('unknown or conflicting source')
    if receipt.get('complete') is not True or not callable(verify_receipt) or verify_receipt(receipt) is not True:
        raise BatchError('independent complete source receipt required')
    if not callable(verify_mapping) or verify_mapping(mapping) is not True:
        raise BatchError('independently reviewed field map required')
    hashes=receipt.get('record_hashes')
    records=batch.get('records')
    if (not isinstance(hashes,dict) or not isinstance(records,list) or len(records)>MAX_RECORDS):
        raise BatchError('unbounded or incomplete record inventory')
    ids=[v.get('record_id') for v in records if isinstance(v,dict)]
    if (len(ids)!=len(records) or any(not isinstance(k,str) or not k for k in ids)
        or len(set(ids))!=len(ids) or set(ids)!=set(hashes)):
        raise BatchError('record population differs from accepted receipt')
    products=[]
    used_bytes=0
    quality={};paths=set();mapped=set()
    for row in records:
        raw64=row.get('raw_base64');expected=hashes.get(row['record_id'])
        if not isinstance(raw64,str) or not isinstance(expected,str) or row.get('sha256')!=expected:
            raise BatchError('source byte receipt mismatch')
        try:raw=base64.b64decode(raw64,validate=True)
        except (ValueError,base64.binascii.Error) as exc:
            raise BatchError('invalid source binary encoding') from exc
        used_bytes+=len(raw)
        if used_bytes>MAX_BATCH_BYTES:raise BatchError('unbounded source batch')
        src=occ.expand(raw,source_id=source,record_id=row['record_id'],
          source_sha256=expected,verify_source=lambda s,r,h: hashes.get(r)==h)
        item=product.project(src,mapping,verify_map=lambda m: True)
        products.append(item)
        paths.update(item['all_source_paths'])
        mapped.update(item['mapped_observed_paths'])
        for name,data in item['fields'].items():
            quality.setdefault(name,Counter()) [data['status']]+=1
    summary={
        'schema':'careops-rims.retained-batch-coverage/1',
        'source':source,'records':len(products),
        'field_quality':{name:{state:quality[name][state] for state in ('present','null','missing')}
                         for name in sorted(quality)},
        'source_paths_observed':len(paths),
        'mapped_observed_paths':len(mapped),
        'unmapped_paths':sorted(paths-mapped),
        'accepted_receipt_custody':'external_verified_callback',
        'native_usage_verified':False,
        'full_provider_capture_verified':False,
        'private_field_names':True,
    }
    return {'schema':'careops-rims.private-retained-products/1',
            'source_id':source,'products':products,'summary':summary,
            'private_values':True,'native_publish_authorised':False,
            'review_status':'NeedsReview'}
