# CareOps delivery pipeline

This is a reusable source blueprint. The private deployment profile and existing
systems define actual accounts, approval rights, delegation and escalation rules.

1. **Intake** — a qualified adapter identifies candidate requests in the selected
   source. Raw message content and operational records remain in the tenant.
2. **Private review** — authorised submitters and the assigned approver use the
   minimum decision context. Any urgent delegation and escalation follow the
   applicable private role mapping and configured deadline, with the accountable
   approver retained. Named people and real routing assignments stay out of this
   portable guide. No email or notification is enabled by this blueprint.
3. **Decision record** — the authoritative register retains decisions and audit
   references. Git contains schemas, contracts, environment-neutral configuration
   and fictional fixtures; it does not contain live decision rows, message bodies,
   clinical narratives or personnel records.
4. **Execution** — use an existing supported API or connector with verified target
   access. Intranet browser or desktop automation needs its own selected,
   qualified route and recovery; source configuration alone does not enable it.
5. **Analytics** — a separately qualified adapter emits the minimum process event
   fields: correlation ID, activity, timestamp, role, outcome, template version and
   escalation state. Keep real events in the governed tenant location and preserve
   the authoritative record rather than creating a second decision register.

## Analytics integration

Use the existing versioned Process event interface for queue age, escalation rate,
turnaround, template demand and delegated-decision auditability. Configure deadlines
in the appropriate authoritative layer; illustrative fixture durations are not
organisation-wide policy. Enforce audience access in the deployed analytics system.
Do not ingest email bodies or identifiable subject details into portable fixtures.

Local analysis may explore directly-follows, throughput, rework and deadline
conformance after event-contract and source-identity qualification. Keep synthetic
fixtures in Git and real event logs in governed storage. Minimized event metadata
can still identify people or cases; minimization alone does not make it public.
