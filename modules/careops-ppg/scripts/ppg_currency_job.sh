#!/bin/sh
# Run from the installation root; launchd serializes this job.
set -eu
umask 077
node_bin=$1
adapter=$2
state=$3
case "$state" in .local/*) ;; *) exit 2;; esac
test -f "$state/current.json"
out="$state/run-$(date +%Y%m%d%H%M%S)-$$.json"
"$node_bin" scripts/ppg_policy_currency.mjs "$adapter" "$out" "$state/current.json" --new-only
mv -f "$out" "$state/current.json"
