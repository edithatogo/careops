"""Reviewed private source-attribute projections from retained JSON occurrences.

A product is never authorisation to publish, issue or infer employment, awards,
organisational affiliation, funding eligibility or clinical impact.
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from collections import defaultdict
import re

if __package__:
    from . import rims_json_occurrences as occ
else:
    _spec=spec_from_file_location('rims_json_occurrences',Path(__file__).with_name('rims_json_occurrences.py'))
    occ=module_from_spec(_spec)
    _spec.loader.exec_module(occ)

_DOMAINS=frozenset({'publications','people','organisations','projects_studies','funding','shared'})
_KINDS=frozenset({'string','integer','number','boolean','null','array','object'})
_TRANSFORMS=frozenset({'identity','doi','integer','date'})
_KEY=re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$')
_DOI=re.compile(r'10\.\d{4,9}/\S+\Z',re.I)

class ProjectionError(ValueError):pass

def _text(value,label):
    if not isinstance(value,str) or not value.strip():raise ProjectionError('missing '+label)
    return value

def _transform(value,transform):
    if value is None:return None
    if transform=='identity':return value
    if transform=='doi':
        if not isinstance(value,str):raise ProjectionError('DOI must be string')
        out=re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:)', '',value.strip(),flags=re.I).lower()
        if not _DOI.fullmatch(out):raise ProjectionError('malformed DOI')
        return out
    if transform=='integer':
        if type(value) is int:return value
        if isinstance(value,str) and re.fullmatch(r'0|[1-9][0-9]*',value):return int(value)
        raise ProjectionError('not an exact integer')
    if transform=='date':
        from datetime import date
        if not isinstance(value,str):raise ProjectionError('date text required')
        try:
            if date.fromisoformat(value).isoformat()!=value:raise ValueError()
        except ValueError as exc:raise ProjectionError('not canonical ISO date') from exc
        return value
    raise ProjectionError('unsupported transform')

def project(projection,mapping,*,verify_map=None):
    if not isinstance(projection,dict) or not isinstance(mapping,dict):
        raise ProjectionError('source and contract required')
    if projection.get('private_values') is not True or projection.get('native_admission_authorised') is not False:
        raise ProjectionError('retained source projection not qualified')
    if mapping.get('schema')!='careops-rims.field-product-map/1':raise ProjectionError('wrong contract')
    if mapping.get('source_id')!=projection.get('source_id'):
        raise ProjectionError('cross-provider source mismatch')
    domain=_text(mapping.get('domain'),'domain')
    if domain not in _DOMAINS:raise ProjectionError('unknown domain')
    revision=_text(mapping.get('revision'),'mapping revision')
    if not callable(verify_map) or verify_map(mapping) is not True:
        raise ProjectionError('mapping not independently reviewed')
    # This recomputes the semantic digest, refuses altered or incomplete occurrences.
    source_record=occ.reconstruct(projection)
    declarations=mapping.get('fields')
    if not isinstance(declarations,list) or len(declarations)>3000:raise ProjectionError('unbounded mapping')
    by_semantic=defaultdict(list)
    for entry in projection['occurrences']:
        by_semantic[entry['semantic_path']].append(entry)
    field_by_name={};source_used=set();all_paths=set(by_semantic)-{''}
    for declaration in declarations:
        if not isinstance(declaration,dict):raise ProjectionError('invalid mapping entry')
        path=declaration.get('source_path')
        target=declaration.get('target_field')
        kinds=declaration.get('kinds')
        cardinality=declaration.get('cardinality')
        transform=declaration.get('transform')
        if not isinstance(path,str) or not path.startswith('/') or len(path)>2048:
            raise ProjectionError('invalid source path')
        if not isinstance(target,str) or not _KEY.fullmatch(target) or target in field_by_name:
            raise ProjectionError('duplicate/invalid target')
        if not isinstance(kinds,list) or not kinds or not set(kinds).issubset(_KINDS):
            raise ProjectionError('invalid source types')
        if cardinality not in ('one','many') or transform not in _TRANSFORMS:
            raise ProjectionError('invalid cardinality or transform')
        observed=by_semantic.get(path,[])
        if cardinality=='one' and len(observed)>1:
            raise ProjectionError('repeated source value cannot be collapsed to scalar')
        values=[]
        for field in observed:
            if field['kind'] not in kinds:raise ProjectionError('unexpected observed source type')
            if field['kind'] in ('array','object') and transform!='identity':
                raise ProjectionError('container cannot be cast')
            value=field['value']
            if field['kind'] in ('array','object'):
                value=source_record
                for token in field['ordered_path'].split('/')[1:]:
                    token=token.replace('~1','/').replace('~0','~')
                    value=value[int(token)] if isinstance(value,list) else value[token]
            values.append(_transform(value,transform))
        if not values:status='missing';value=None if cardinality=='one' else []
        elif cardinality=='one':
            value=values[0];status='null' if value is None else 'present'
        else:
            value=values;status='present'
        field_by_name[target]={
            'status':status,'value':value,'source_path':path,'source_kind':list(kinds),
            'cardinality':cardinality,'mapping_revision':revision,
            'source_ordinals':[r['ordered_path'] for r in observed],
        }
        if observed:source_used.add(path)
    # Original occurrence projection is retained verbatim in a private-only product.
    return {
        'schema':'careops-rims.private-field-product/1',
        'source_id':projection['source_id'],'source_record_id':projection['record_id'],
        'source_sha256':projection['source_sha256'],
        'mapping_revision':revision,'domain':domain,'fields':field_by_name,
        'all_source_paths':sorted(all_paths),
        'mapped_observed_paths':sorted(source_used),
        'unmapped_source_paths':sorted(all_paths-source_used),
        'source_occurrences':projection,
        'private_values':True,'native_publish_authorised':False,
        'review_state':'NeedsReview','report_issued':False,
        'source_field_utilisation_native_verified':False,
    }
