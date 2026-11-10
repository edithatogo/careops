# Reusable meeting system — 10 November 2026

**Status:** source increment implemented; native and multi-forum runtime qualification open.
**Owner:** Decisions owns governance records; Clinical Hub owns the optional preparation/workspace experience. Standalone Clinical Hub selects a local record provider. No physical relocation or database migration is authorised by this track.

## Goal
Configure many independent governance meetings from versioned, explicit forum profiles without cloning flows, lists or custom business logic for each forum. Reuse existing H2 profile/occurrence resolution, paper preparation, minutes review, linked decisions/actions and recoverable correspondence. A shared Decisions register must retain one authoritative identity per decision/action; a forum identifier forms part of every occurrence/link key.

Core is standard Microsoft 365 (SharePoint Lists and Libraries, standard Outlook/SharePoint Power Automate operations, native forms and maintained Word templates). **No Copilot, AI Builder, premium Power Automate, HTTP/custom connector, Dataverse or paid AI dependency**. Optional extensions are separately selected and cannot prevent core installation. Python is a maker/test helper, not a production runtime.

[Requirements](requirements.md) · [Design](design.md) · [Executable tasks](plan.md)

## Completed source slice
- [x] RMS-01 Existing H2 forum_configuration/profile resolution reused and boundaries recorded.
- [x] RMS-02 A pure deterministic multiple-forum blueprint compiler with sorted stable SHA-256 output, strict input fields and independent forum namespaces.
- [x] RMS-03 Focused fictional tests for multiple forums, canonical ordering, duplicate identities, rejected Copilot/unknown bindings, and no implied writes.
- [ ] RMS-04 Canonical CI and repository/parent source/privacy/compatibility checks on exact PR head, then protected merge (hosted Actions capacity may block).
- [ ] RMS-05 Real Decisions standard SharePoint provider adapter and one authoritative action/decision register; standalone local-provider equivalence.
- [ ] RMS-06 Operator configuration and repeatable installation for two independent fictional forums; full real native binding/permission/race/recovery checks.
- [ ] RMS-07 Evaluate meeting cycle and usability/administrative burden against a manual baseline; no effect claims before measurements.
- [ ] RMS-08 Optional OCEL/provenance exports and AI assistance only after governed records and source fidelity pass.

This track does not reopen completed correspondence packaging CHG-01/02 or claim H2 bridge runtime release; preserve H2-N03–05 and H1 governance gaps in their original tracks.

## 10 November source continuation

Implemented `meeting_register_projection.py` as a read-only source-qualified **shape** for shared-register views. Seven isolated Python 3.13 focused tests passed; exact PR-head canonical CI and native provider acceptance remain outstanding. This does not replace F09/F15 or grant any user role, minute approval or action closure. Next track item is RMS-05b: verify real standard SharePoint register reads with all pages and known owner, then native two-forum reuse. Do not treat status counts as authenticated governance outcomes.
