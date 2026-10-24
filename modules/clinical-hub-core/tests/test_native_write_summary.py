from copy import deepcopy
import pytest
from scripts.native_write_lifecycle import definition, definition_summary, summary_entry_multisets


def graph():
    return dict(actions={'first':dict(type='Compose',inputs='fixture')},triggers={
        'manual':dict(type='Request',kind='Button',inputs={})})


def test_summary_preserves_duplicates_and_unknown_shapes_never_authorize_changes():
    g=graph();before=deepcopy(g);summary=definition_summary(g)
    assert g==before
    reordered={k:list(reversed(v)) for k,v in summary.items()}
    assert summary_entry_multisets(summary)==summary_entry_multisets(reordered)
    doubled=deepcopy(summary);doubled['actions']*=2
    assert summary_entry_multisets(summary)!=summary_entry_multisets(doubled)
    g['actions']['first']['type']='OpenApiConnection'
    assert definition_summary(g) is None
    assert summary_entry_multisets({'actions':[]}) is None
    assert definition_summary({'actions':{},'triggers':{},'unknown':True}) is None


def test_known_auth_normalization_is_narrow_and_does_not_mutate_source():
    g=graph();g['actions']['first']=dict(type='OpenApiConnection',inputs={'authentication':"@parameters('$authentication')"})
    before=deepcopy(g);normal=definition(g)
    assert 'authentication' not in normal['actions']['first']['inputs'] and g==before
    g['actions']['first']['inputs']['authentication']='Unknown private binding'
    with pytest.raises(RuntimeError):definition(g)
