# Native workflow candidates and Canvas safety review — 12 November 2026

**Scope:** local authoring and static validation only. **No tenant deployment, Power Apps Studio validation, SharePoint authentication, cloud-flow activation or solution ZIP import claimed.** CareOps Workforce owns the operational application, not CareOps-PPG.

## Delivered source

- [Three SharePoint Standard, read-only WDL candidates](../../../../careops-workforce-app/flows/native-candidates/README.md): hourly prepared-operation count, daily due-obligation bounded monitor, and hourly minimal plan-head connectivity check.
- [Power Automate WDL definitions](../../../../careops-workforce-app/flows/native-candidates/) with Recurrence triggers, one real `shared_sharepointonline` `HttpRequest` GET each, bounded `$top=100` query, minimal result projection, and `Terminate` Failed on connector errors.
- [Four offline test cases for native candidates](../../../../careops-workforce-app/tests/test_native_flow_candidates.py) asserting read-only standard connector, dependencies, no tenant URLs/tokens, no response exposure, proper fail-run behaviour and no accidental activation. Tests committed; exact-head Python CI has not passed.
- [Canvas role and draft guard tests](../../../../careops-workforce-app/tests/test_canvas_role_hints.py). Home, approver and operator screen review specifications now default privileged visibility false until a trusted role projection is bound. The generated app initialises role flags false. The Save Draft button now warns that no persistence exists rather than fabricating a saved confirmation.
- [Updated source generator](../../../../careops-workforce-app/tools/generate_source.py) retains these guards on regeneration.
- [Expanded GitHub Actions](../../../../../.github/workflows/workforce-jobplan-sharepoint.yml) to execute full offline app suite, candidate tests, and skill checks (requires PyYAML); last CI evidence cannot be treated as passing due to previously unavailable runners.

## Qualification evidence

The three current JSON definitions were reread from the exact GitHub branch and independently checked in the current session for JSON parse, WDL root fields, valid action dependencies, Recurrence trigger, SharePoint `HttpRequest` GET only, and failed-run termination. **Three of three passed these static assertions.** Six Canvas screen specifications plus generator were reread and checked for role flags and truthful draft messaging. These checks are useful static evidence; they are **not** `pac` import, WDL schema tooling, native connector or role access qualification. The 4+4 Python test cases were added but no passing Python test run was observed for this branch in this session.

## Safety and functional boundaries

The candidates intentionally **do not mutate SharePoint**, send reminders, approve cases or activate future-effective versions. Their first-page limits mean they **cannot certify completeness** for larger queues. The activation-readiness file is presently only a **plan-head connectivity check**, not a due/approval eligibility filter. The approved current version remains governed by the reference engine and native authorisation requirements.

Existing `flows/01-*.workflow.json` through `10-*.workflow.json` remain intentionally disabled privileged scaffolds. This is not a native, solution-aware flow package. Authentic privileged flows must verify caller identity server-side, acting roles, HR/IR consultation, service scope, rule edition, immutable digest, SharePoint exact ETag, idempotent operation receipts, failure recovery and list/document-library ACL. **Never substitute Power Apps visibility for SharePoint permissions.**

The Canvas `.pa.yaml` are **reviewable specifications**, not Studio-originated round-trip-validated app source; the maker must bind the trusted role projection before any real use. When unset, privileged navigation is hidden and mock Save Draft is explicitly non-operational.

## Next implementation tasks

1. **JP-NF04:** bind restricted development SharePoint Standard connection to real list ids, validate these read-only workflows in an authorised nonproduction Power Platform solution, pagination and 429/412/error behaviour.
2. **JP-NF05:** create solution-aware privileged submit/decision/activation/rollback flows using trusted identity/delegation and staging/conditional update protocol; remove inert Compose actions only when each real action is verified.
3. **JP-NF06:** Canvas Studio-authoring source integration, role-projection flow and actual save/submit APIs; test practitioner-only, approver-only, dual-role and revoked-permission scenarios at both UI and data layers.
4. **JP-NF07:** run complete GitHub CI on exact head, Python unit tests, platform checker and import/reimport/rollback in authorised dev tenant. No branch-protection bypass.
5. **JP-NF08:** tenant-specific SharePoint data classification, records/retention/legal hold, confidential exports and service-level permission scalability qualification.

Original CHHHS job planning documents and individual schedules remain outside the Git repository.
