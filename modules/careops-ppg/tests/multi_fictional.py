"""Generate multi-edition test inputs from the independently compiled fictional fixture."""
import json

from scripts.ppg_completed_relationship_assessment import catalogue_snapshot, relationship_snapshot
from scripts.ppg_multi_edition import prepare_multi_completion
from tests.test_multi_edition import sample


def fictional_case():
    inputs = sample()
    return {
        'transition': prepare_multi_completion(**inputs),
        'context': {
            'relationships': relationship_snapshot(inputs['relationships']),
            'catalogue': catalogue_snapshot(inputs['catalogue']),
        },
    }


if __name__ == '__main__':
    print(json.dumps(fictional_case()))
