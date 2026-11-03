#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu
umask 077
cd "$(dirname "$0")/.."
py=.local/validation/venv/bin/python
test "$("$py" --version)" = 'Python 3.15.1'
mkdir -p .local
run=$(mktemp -d .local/bootstrap.XXXXXX)
echo "Local bootstrap directory: $run"
export PYTHONPATH=src
packet=examples/packet.json
"$py" -m careops_improvement.cli "$run/register.sqlite" import "$packet" > "$run/import.json"
"$py" -m careops_improvement.cli "$run/register.sqlite" report > "$run/projection.json"
"$py" tools/provisioning.py dry-run > "$run/sharepoint-teams-plan.json"
"$py" -m careops_improvement.cli "$run/register.sqlite" export --kind process-mining --output "$run/process-mining.csv"
"$py" tools/build_flows.py --output-dir "$run/flows"
"$py" tools/build_analytics.py "$packet" "$run/analytics" > "$run/analytics-receipt.json"
"$py" tools/report_pack.py "$run/projection.json" "$run/print" --period 2026-11
sh tools/pack_solution.sh "$run/solution"
echo "Completed fictional local bootstrap: $run"
