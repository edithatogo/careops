# CareOps delivery pipeline

1. **Email intake** — Power Automate identifies TESL candidates in the owner's
   mailbox; raw message content remains in Microsoft 365.
2. **Private approval** — the submitter and assigned approver receive only the
   minimum decision context. Natalie Degidio and Kathryn Meharg may submit,
   edit, and use documented urgent verbal delegation; the TESL approver remains
   accountable. Unapproved items escalate after 14 days to Elaine Pretorius.
3. **Decision record** — store decision metadata and audit references, not
   clinical or personnel narrative, in source-controlled configuration.
4. **Intranet execution** — defer desktop automation until a supported gateway,
   machine, or approved connector is discovered. Treat browser/RPA work as a
   separate controlled track.
5. **Analytics** — export a de-identified event log containing case ID, activity,
   timestamp, role, outcome, template, and escalation state.

## Analytics recommendation

Power BI improvement is warranted for queue age, escalation rate, turnaround,
template demand, and delegated-decision auditability. Build a small semantic
model over de-identified decision metadata and enforce row-level access outside
the repository. Do not ingest email bodies or identifiable subject details.

Local `pm4py` analysis is also warranted once the event contract is stable and
there are enough cases. Start with directly-follows, throughput, rework, and
14-day escalation conformance. Use synthetic fixtures in Git; retain real event
logs only in the governed tenant storage location.
