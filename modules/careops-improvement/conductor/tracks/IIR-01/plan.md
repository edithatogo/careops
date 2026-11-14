# Local implementation and acceptance

- [x] Specify governance routes, delegated decision ownership and the boundary between registration and commencement authority.
- [x] Implement the portable register and governance-route validation; the module's 34 local tests pass across source, platform and packaging checks.
- [ ] Obtain local governance-owner review of route mappings, decision ownership and policy fit.
- [ ] Qualify exact native SharePoint resources, permissions, save/readback and audit behavior before deployment.
- [ ] Keep any pilot or commencement decision separately authorized.

Local tests establish behavior of the fictional/local implementation only. They do not establish policy approval, native behavior or authority to commence work. See the module README and [platform acceptance scope](../../../../platform/README.md).

Local review found that a pending decision could carry a decision timestamp and a decision could predate submission. The packet importer now checks UTC timestamps and rejects inconsistent chronology atomically. The focused register suite covers rollback. Local governance owner mapping and native access verification remain open.

Local sprint verification: Governance routes and decision chronology were exercised through the register suite. The two bootstrap runs preserved the same decisions.
