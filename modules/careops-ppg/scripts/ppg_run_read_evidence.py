"""Project successful fictional run reads separately from static flow bindings."""
from collections import defaultdict


def apply_run_reads(manifest, workflow_names, evidence, external_datasets):
    if not evidence:
        return
    candidates = {(row['flow'], row['action']) for row in manifest['unresolvedActions']
                  if 'FICTIONAL' in row['flow'] and row['operation'] == 'HttpRequest'}
    recorded, counts = {}, defaultdict(lambda: defaultdict(set))
    for item in evidence:
        flow = workflow_names.get(item['flowId'].lower())
        action, run, dataset = item['action'], item['run'], item['dataset'].lower()
        if (flow != item['flow'] or (flow, action) not in candidates
                or item['method'] != 'GET' or not run or not item['fileId']
                or item['actionStatus'] != 'Succeeded' or item['runStatus'] != 'Succeeded'):
            raise ValueError('Run evidence does not match a successful fictional read')
        if dataset not in manifest['rows'] and dataset not in external_datasets:
            raise ValueError('Run evidence requires a verified parent dataset')
        key = (flow, action, run)
        if key in recorded and recorded[key] != item:
            raise ValueError('Conflicting action evidence for a run')
        recorded[key] = item
        counts[dataset][flow].add(action)
    observed = {(flow, action) for flow, action, _ in recorded}
    manifest['unresolvedActions'] = [row for row in manifest['unresolvedActions']
                                      if (row['flow'], row['action']) not in observed]
    manifest['fictionalRunReads'] = list(recorded.values())
    for ident, row in manifest['rows'].items():
        lines = [f'{flow}: {len(actions)} reads observed in retained runs'
                 for flow, actions in sorted(counts[ident].items())]
        row['ObservedReadFlows'] = '\n'.join(lines) or None
