# N01 plan: platform and independently installable packages

Owner: Platform architect, to be named. In progress; no tenant completion claimed.

- [~] N01.01 Inventory actual tenant, environments, licences, capacity and residency; accept a signed prerequisites/gaps record, not assumed entitlements.
- [ ] N01.02 Agree service owner, business impact, RPO/RTO and downtime targets; accept separately labelled proposed targets and local approval.
- [~] N01.03 Define development/test/production/recovery boundaries and shared-versus-separate module environments; accept documented security and restore blast radius.
- [ ] N01.04 Inventory every existing solution component and dependency; accept a per-module ownership map with no hidden shared business table.
- [ ] N01.05 Build core managed-solution packaging and separate adapter packages; accept no sibling lookups, flow references or mandatory shared runtime in core exports.
- [ ] N01.06 Set connection references, environment variables and non-personal production ownership; accept least-privilege bindings and owner-departure tests.
- [ ] N01.07 Enforce stable required GitHub checks and force-push/deletion controls via authorised administration; accept actual settings receipts, retaining solo-maintainer operation.
- [ ] N01.08 Produce reproducible versioned artifacts, dependency inventory and rollback package; accept build provenance and no environment secrets in source.
- [ ] N01.09 Install each core alone in a clean approved sandbox; accept seven individually recorded business-scenario and dependency-inspection results.
- [ ] N01.10 Rehearse upgrade, adapter removal and data-preserving retirement; accept no sibling failure or silent data deletion, then publish install/support instructions.

## Source implementation, 23 September 2026

Added [pilot preflight](../../../scripts/pilot_profiles.py) and
[no-admin pilot](../../../docs/credentialing/no-admin-pilot.md). Existing M365
Lists and standard SharePoint flows are separate synthetic pilot profiles, with
no new Entra app or operator tenant-admin requirement. Full Dataverse remains
the production target. Local Python 3.13.5: 12 behavioural methods; 60 statements
and 12 branches, 100%. Final-head remote static/test results belong in the PR.

Remaining gates: actual site/maker/connector observations; approved production
environments/licences/owners; enforced repository rules; clean native installs;
recovery and retirement evidence. No self-reported preflight confers permission.
Close tasks with artifact/PR, result, reviewer and date. Archive a completed source
slice separately, never this parent track while these requirements remain open.
