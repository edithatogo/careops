#!/usr/bin/env bash
# CareOps workspace-only setup for the existing exact-pinned upstream Conductor.
# Does not install software globally or initialise/overwrite conductor/ tracks.
set -euo pipefail

usage() {
  printf 'Usage: %s [--verify|--link]\n' "$0"
  printf '  --verify  Check pinned submodule and host prerequisites (default)\n'
  printf '  --link    Initialise pinned submodule and link its Agent Skills into this Gemini workspace\n'
}
mode="${1:---verify}"
case "$mode" in
  --verify|--link) ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

root="$(git rev-parse --show-toplevel)"
cd "$root"
path=".agents/plugins/conductor"
expected="$(git rev-parse "HEAD:$path")"
if [[ ! "$expected" =~ ^[0-9a-f]{40}$ ]]; then
  echo "No gitlink at $path; refusing an unpinned installation" >&2
  exit 1
fi
if [[ "$mode" == "--link" ]]; then
  git submodule update --init --checkout -- "$path"
fi
if [[ ! -f "$path/skills/conductor-setup/SKILL.md" ]]; then
  echo "Pinned Conductor is not initialised. Run git submodule update --init --checkout -- $path" >&2
  exit 1
fi
actual="$(git -C "$path" rev-parse HEAD)"
if [[ "$actual" != "$expected" ]]; then
  echo "Conductor checkout differs from parent gitlink: $actual != $expected" >&2
  exit 1
fi
if ! command -v gemini >/dev/null 2>&1; then
  echo "Gemini CLI is not installed on this host; upstream submodule verified, workspace activation unavailable." >&2
  exit 2
fi
gemini --version
if [[ "$mode" == "--link" ]]; then
  count=0
  for skill in "$root/$path"/skills/*; do
    [[ -f "$skill/SKILL.md" ]] || continue
    gemini skills link "$skill" --scope workspace
    count=$((count + 1))
  done
  [[ "$count" -gt 0 ]] || { echo "No upstream Agent Skills found" >&2; exit 1; }
fi
gemini skills list --all
echo "Conductor gitlink: $expected"
echo "Conductor source verified. In the Gemini CLI session reload skills and verify activation."
