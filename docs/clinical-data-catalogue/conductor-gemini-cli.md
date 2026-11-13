# Using upstream Conductor unmodified with Gemini CLI

**Status:** documented installation/qualification procedure. Actual local Gemini CLI activation has not been run in this source-only PR.

CareOps already tracks `gemini-cli-extensions/conductor` at `.agents/plugins/conductor` (gitlink SHA recorded in the reviewed `PUBLIC_SOURCE_FILES.json`). Do **not** add a second submodule, vendor the skills, create a fake `gemini-extension.json`, or edit upstream files.

## Supported strategy: Gemini CLI workspace Agent Skills

Gemini CLI discovers native Agent Skills from workspace `.agents/skills` or `.gemini/skills`, and supports `gemini skills link <path> --scope workspace`. This is distinct from Gemini CLI **extensions**. Upstream Conductor has `skills/*/SKILL.md` and a `plugin.json`, but currently no `gemini-extension.json`; do not assume `gemini extensions install` will activate it.

For a clean clone, a workspace-only helper is now available:

```sh
bash scripts/setup_gemini_conductor.sh --verify
bash scripts/setup_gemini_conductor.sh --link
```

The helper checks the exact parent gitlink, initialises the pinned submodule on `--link`, links upstream Agent Skills to the current Gemini workspace, and lists discovered skills. It never rewrites existing `conductor/` tracks. Host activation still requires a Gemini CLI installation and explicit local verification.

Manual equivalent, after a clean clone:

```sh
git submodule update --init --checkout -- .agents/plugins/conductor
git submodule status -- .agents/plugins/conductor
git ls-tree HEAD .agents/plugins/conductor
gemini --version
for skill_dir in .agents/plugins/conductor/skills/*; do
  test -f "$skill_dir/SKILL.md" || continue
  gemini skills link "$skill_dir" --scope workspace
done
gemini skills list --all
```

Review the link command output and workspace state before committing any generated files; linked skill paths are *local host configuration*, not a second source dependency. Do not globally activate the project skills or commit machine-specific absolute symlink paths.

In the Gemini CLI session, run `/skills reload` (or restart), confirm `conductor-setup`, `conductor-new-track`, `conductor-status`, `conductor-implement` are discoverable, and request activation in a **fictional test workspace**. Inspect consent prompts and ensure the skill reads the intended project-specific `conductor/` context. A tool/host-specific instruction in upstream skills may still require adaptation or fail; record its exact behavior instead of editing vendor code.

The upstream slash commands `/conductor:conductor-setup` and `/conductor:conductor-implement` are plugin-host syntax; Gemini CLI native Agent Skills may instead be activated by natural-language task requests or `activate_skill`. Do not promise identical slash-command behavior across hosts.

## Admission and update tests

1. Exact upstream gitlink and licensing receipt.
2. Linked skill names, successful list/reload and activation receipt in Gemini CLI version under test.
3. Create/inspect a fictional track; confirm no overwrite of existing `conductor/tracks.md`.
4. Run negative tests: absent submodule, incompatible host version, duplicate skill name, denied activation, path containment, and changes to upstream files.
5. Demonstrate rollback: remove locally linked skills using supported Gemini CLI commands, keep parent gitlink unchanged.
6. Update upstream only by an independently reviewed parent gitlink PR. Any required adapter belongs to project-owned source, not `.agents/plugins/conductor`.

Official source: https://geminicli.com/docs/cli/skills/ and https://geminicli.com/docs/cli/using-agent-skills/ .
