# Locally authored SharePoint Standard WDL candidates

**Status:** three **read-only** authored Workflow Definition Language candidates, static source validation only. Not solution-aware exported flows, imported flows, tenant-tested flows, or activated automations. They are separate from the ten intentionally disabled privileged workflow scaffolds in `../*.workflow.json`.

| Candidate | Trigger | SharePoint Standard HTTP GET | Outcome | Limitation |
|---|---|---|---|---|
| `01-operations-monitor.json` | hourly | `JP_Operations` status `Prepared` | count prepared operation records | first 100 only; not an automated repair worker |
| `02-review-due-monitor.json` | daily | `JP_ReviewObligations` status `Open` | filter returned due dates against current UTC and count | first 100 only; does not issue review cases or reminders |
| `03-activation-readiness-monitor.json` | hourly | `JP_PlanHeads` minimal projection | counts available heads to check connector/read path | does **not** determine whether a scheduled approval is due, and never activates |

All use only `shared_sharepointonline` connector action `HttpRequest` with `GET`, and a required environment-bound `SharePointSiteUrl` placeholder. Failed or timed-out SharePoint reads use an explicit failed-run termination, rather than producing a misleading success. The source contains no tenant URL, passwords, tokens, e-mail recipients or private plan payload.

## Binding and qualification

1. In a **development** Power Platform solution, create scheduled cloud flows using approved, service-owned SharePoint Standard connection references. Author with the environment selected by CHHHS; bind `SharePointSiteUrl` to an approved environment variable.
2. Import or recreate the WDL definition using supported native tooling; verify actual supported connector action IDs, expressions and recurrence.
3. Configure site/list permissions so the flow can read only its minimum required metadata. Do not grant blanket organisation-wide read to employee records or use a Canvas user-supplied UPN as authorisation.
4. Run schema/source checker and **real** tenant execution including authentication, pagination, SharePoint throttling/429, empty list, malformed date, clock/time zone, and failure paths.
5. Add bounded pagination or indexed partitioning before interpreting counts as complete. Never use these monitoring candidates to decide industrial or clinical outcomes.
6. Use independent review/authority/HRIR contracts to implement **privileged mutation flows**. Do not change the ten disabled workflow scaffolds to active based on these monitors.

## Offline verification

`python -m unittest discover -s tests -p test_native_flow_candidates.py -v`

The corresponding CI job runs all offline app tests via `tools/check_all.sh`; GitHub Actions passing status must be separately observed. These sources are not valid `.msapp` binaries or proof of imported Power Platform cloud flows.
