#!/usr/bin/env bash
set -euo pipefail
module_root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "$module_root" != "$(git rev-parse --show-toplevel)" ]]; then
  echo 'CareOps owns hooks for the integrated module; retain parent hooks and CI.' >&2
  exit 1
fi
cd "$module_root"
existing=$(git config --get core.hooksPath || true)
if [[ -n "$existing" && "$existing" != '.githooks' ]]; then
  echo "Existing hooksPath retained: $existing. Compose its hooks with scripts/check_secrets.sh." >&2
  exit 1
fi
if [[ -z "$existing" ]]; then
  for hook in pre-commit pre-push; do
    if [[ -f "$(git rev-parse --git-path hooks)/$hook" ]]; then
      echo "Existing $hook retained; compose with scripts/check_secrets.sh." >&2
      exit 1
    fi
  done
fi
git config core.hooksPath .githooks
echo 'Installed staged-snapshot and pre-push history scans.'
