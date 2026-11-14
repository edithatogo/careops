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
for kind in lists library; do
    "$py" tools/provisioning.py "reconcile-$kind" --inventory platform/sharepoint/schema.json > "$run/$kind.json"
done
team=12345678-1234-4234-8234-123456789abc
channel=19:fictional@thread.tacv2
printf '{"team_id":"%s","channel_id":"%s","tabs":[]}\n' "$team" "$channel" > "$run/channel.json"
"$py" tools/provisioning.py reconcile-teams --inventory "$run/channel.json" --team-id "$team" --channel-id "$channel" --sharepoint-list-url https://contoso.sharepoint.com/sites/demo/Lists/Initiatives > "$run/tab.json"
feed() { "$py" -m careops_improvement.cli "$run/feeds.sqlite" "$@"; }
feed feed-import excel demo examples/feeds/initiatives.csv > "$run/feed-initiatives.json"
feed feed-import planner demo examples/feeds/tasks.json > "$run/feed-tasks.json"
feed feed-import sharepoint demo examples/feeds/events.json > "$run/feed-events.json"
feed feed-import sharepoint demo examples/feeds/events.json > "$run/feed-replay.json"
feed report > "$run/feed-report.json"
feed export --kind process-mining --output "$run/feed-events.csv"
"$py" tools/build_flows.py --output-dir "$run/flows"
"$py" tools/build_analytics.py "$packet" "$run/analytics" --period 2026-11 > "$run/analytics-receipt.json"
"$py" tools/report_pack.py "$run/analytics/frozen-projection.json" "$run/print" --period 2026-11
sh tools/pack_solution.sh "$run/solution"
echo "Completed fictional local bootstrap: $run"
