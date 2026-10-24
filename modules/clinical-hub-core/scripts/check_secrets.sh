#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
command -v gitleaks >/dev/null || { echo 'Gitleaks is required before commit/push.' >&2; exit 1; }
case "${1:-staged}" in
  staged)
    snapshot=$(mktemp -d)
    trap 'rm -rf "$snapshot"' EXIT
    git checkout-index --all --prefix="$snapshot/"
    # Never publish operational caches, credentials or private records.
    if git ls-files | LC_ALL=C grep -E '(^|/)(private|\.flowagent|\.vscode|\.venv[^/]*|\.env)(/|$)|\.(token|pem|pfx)$'; then
      echo 'Private/runtime material is tracked; remove it from the index before publishing.' >&2
      exit 1
    fi
    gitleaks dir "$snapshot" --redact --no-banner
    ;;
  history) gitleaks git --redact --no-banner ;;
  *) echo 'Usage: check_secrets.sh staged|history' >&2; exit 2 ;;
esac
