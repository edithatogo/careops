# Pilot without tenant administration or a new Entra application

23 September 2026. N01 source delivery; programme edithatogo/careops#160.
Full production remains Dataverse. The pilot is not a replacement register,
a permission bypass or a production approval route.

## Independently selectable pilot routes

| Route | Existing permissions required | Current source delivery |
| --- | --- | --- |
| Lists rehearsal | Work account; permitted service-owned SharePoint site and list/view management; reviewed membership | Synthetic CSV and native column formatting in careops-approve#57 |
| Built-in Flow rehearsal | Work account; existing flow-maker entitlement and policy permission | Connector-free instant-flow definition and designer runbook in careops-approve#57 |
| Standard SharePoint flow pilot | Lists permissions plus flow-maker and permitted standard SharePoint connection/data policy | Preflight/profile only; connected worker is not yet delivered |

The first two routes do not require each other. Neither requires a custom Entra
application, supplied app ID, operator tenant-administrator role, Dataverse,
custom connector, premium AI or another CareOps module. The flow uses native
built-in actions and fixed synthetic cases only. Existing Microsoft sign-in,
permissions, licensing and policies still apply; unknown is not permission.

The install source and steps are at:
https://github.com/edithatogo/careops-approve/tree/main/pilot/m365
Operators do not need Python. Its generator and preflight are developer tests.

The `scripts/pilot_profiles.py` preflight never contacts Microsoft, authenticates
an operator or changes a permission. A fallback is offered only when ALL its
requirements were observed true. A blocked flow can leave Lists usable, or a
blocked List can leave the permitted built-in flow usable. If neither is allowed,
retain source-only demonstrations; never move data to an unapproved service.
Even verified production observations lead to deployment review, not activation.

## What this pilot is and is not

Use the supplied eight synthetic cases only. Do not load real CVs, registrations,
names, complaints, patient data or practitioner exports. In Lists, restrict
membership and disable attachments. Label records PILOT / NOT VALID FOR PRACTICE.
The labels are not a mechanism for detecting real information or enforcing access.

Red/amber/green describe preparation, not practitioner suitability. Missing
administrative evidence produces a draft information-request status; simulated
agent concerns require human review. A technical failure is unavailable, not a
practitioner deficiency. The existing reviewer acts once in the same case.
No actual agent, credentialing decision, automatic applicant return, external
correspondence, authoritative register write or roster/access change is enabled.

Column formatting changes presentation, not the stored Assessment value. The
stored value is explicitly DISPLAY ONLY. It is not a production register or an
exportable computed decision. Missing columns, malformed types or rendering
errors fail acceptance; never interpret an absent indicator as green.

The Flow JSON is native source, not a tenant-exported import ZIP. The runbook
contains finite designer setup and save/run steps. Microsoft requires existing
Environment Maker rights for non-solution package imports; do not claim admin-free
means entitlement-free. Native engine execution, keyboard/screen-reader checks
and actual operator permissions are still unverified. Later real-data read-only
observation needs a separately approved privacy/access/source boundary, not a
flag that promotes synthetic records to production.

## Sequential delivery and closure

Use current main as the base after the previous PR has passed, been reviewed and
merged. Across repositories, record predecessor PR and merge commit without a
mandatory runtime dependency. Completed source slices have sanitized close-out
records in the parent track; excluded raw Conductor archives are not published.
Full tracks stay open until their tenant, authority and operational gates pass.
See the N01 and N02 completed-source-slices records for this delivery sequence.

No tenant, new app registration, permissions, licence purchase or operational
record was changed. Full Dataverse, signed authority and M2-M7 gates remain.

## Primary Microsoft documentation

- https://support.microsoft.com/en-us/sharepoint/lists/create-a-list-from-the-lists-app
- https://learn.microsoft.com/en-us/sharepoint/dev/declarative-customization/column-formatting
- https://learn.microsoft.com/en-us/power-automate/export-import-flow-non-solution
- https://learn.microsoft.com/en-us/connectors/sharepoint/
