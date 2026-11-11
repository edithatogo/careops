#!/usr/bin/env bash
# Reviewable local agent-plugin bootstrap. Does not modify the Power Platform tenant.
set -euo pipefail
usage() {
  cat <<'USAGE'
Usage: scripts/power-platform-skill-bootstrap.sh [--check|--copilot|--claude|--checkout-sources]
  --check             Print needed installations, execute nothing (default).
  --copilot           Register Microsoft marketplaces and install four specified plugins.
  --claude            Register Microsoft marketplaces and install four specified plugins.
  --checkout-sources  Clone the four verified repository sources at pinned SHA
                      into ignored .local-agent-marketplaces/ for independent audit.
USAGE
}
case "${1:---check}" in
  --check)
    for cmd in git dotnet copilot claude; do
      if command -v "$cmd" >/dev/null 2>&1; then
        printf '%s: %s\n' "$cmd" "$(command -v "$cmd")"
      else
        printf '%s: unavailable\n' "$cmd"
      fi
    done
    printf '%s\n' 'Plugin setup is local to the agent. No tenant setup or ChatGPT account modification occurs.'
    printf '%s\n' 'See docs/development/power-platform-agent-skills.md for exact sources, versions and caveats.'
    ;;
  --copilot|--claude)
    mode="${1#--}"
    command -v "$mode" >/dev/null 2>&1 || { echo "$mode CLI unavailable" >&2; exit 2; }
    if [ "$mode" = copilot ]; then
      "$mode" plugin marketplace add microsoft/power-platform-skills
      "$mode" plugin marketplace add microsoft/power-cat-skills
      "$mode" plugin install canvas-apps@power-platform-skills
      "$mode" plugin install powercat-canvas-apps@power-cat-skills
      "$mode" plugin install power-automate@power-platform-skills
      "$mode" plugin install dataverse@power-platform-skills
    else
      "$mode" plugin marketplace add microsoft/power-platform-skills
      "$mode" plugin marketplace add microsoft/power-cat-skills
      "$mode" plugin install canvas-apps@power-platform-skills
      "$mode" plugin install powercat-canvas-apps@power-cat-skills
      "$mode" plugin install power-automate@power-platform-skills
      "$mode" plugin install dataverse@power-platform-skills
    fi
    echo 'Plugin installation commands completed; inspect plugin listings and verify authoring MCP access.'
    ;;
  --checkout-sources)
    command -v git >/dev/null 2>&1 || { echo 'git required' >&2; exit 2; }
    root="$(git rev-parse --show-toplevel)"
    mkdir -p "$root/.local-agent-marketplaces"
    while read -r folder repo sha; do
      [ -n "$folder" ] || continue
      target="$root/.local-agent-marketplaces/$folder"
      if [ ! -d "$target/.git" ]; then
        git clone --no-checkout "https://github.com/$repo.git" "$target"
      fi
      git -C "$target" fetch --depth 1 origin "$sha"
      git -C "$target" checkout --detach "$sha"
      actual="$(git -C "$target" rev-parse HEAD)"
      [ "$actual" = "$sha" ] || { echo "Pinned commit mismatch: $repo" >&2; exit 3; }
      echo "Pinned source $repo @ $actual"
    done <<'SOURCES'
power-platform-skills microsoft/power-platform-skills 8021d27d517d81963da22e728125a26c9ecfbbe1
power-cat-skills microsoft/power-cat-skills 3408c7b0ab2414946adcdaf0ba87eb9ca320fcd2
Dataverse-skills microsoft/Dataverse-skills 27e6f6a3fef23075ede87d8e5f028cde29e0130e
claude-power-automate Wals-pro/claude-power-automate a9676c2f00d1645d55a21013105ccb2745860f20
SOURCES
    echo 'Pinned checkouts fetched for audit. No code installed or executed.'
    ;;
  -h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
