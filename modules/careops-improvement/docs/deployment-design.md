# Independent solution and deployment design

`config/resources.json` describes an independently versioned, unmanaged
Power Platform solution plus companion resources. It is a generic design
manifest, not a native solution definition. The solution has its own publisher,
unique name and version. Environment-specific values and connection bindings
must be supplied in a private deployment profile; the portable manifest leaves
environment variables and connection references empty until supported
components and exact references are qualified. A resource may be implemented
outside the solution (SharePoint, Planner, Teams, Excel or BI) and is tracked by
its stable manifest key. The plan utility only compares keys and values from
explicit JSON inputs.

No flow action schema, connector operation, trigger, connection ID or
environment binding is guessed here. Add a flow only after inspecting its
authoritative generator and a valid accepted example, then preserve unknown
properties and verify the parsed semantic change. Prefer standard connectors
and existing qualified routes. Optional external integrations are not required
for the portable baseline.

## CLI-only deployment sequence

1. **Prepare locally:** validate manifest shape and unique resource keys; review
   field names, data types, authority, solution version and module dependencies.
   Generate a dry-run plan from a bounded, explicit target inventory.
2. **Qualify the route:** inspect installed PAC/CLI help and the relevant
   supported operation. Read exact selected environment and solution metadata
   through the retained qualified workload. Verify account, tenant, environment,
   publisher, operation rights and exact target before any write. Login or
   metadata visibility does not prove write permission.
3. **Package:** use the supported solution source and pack operation for the
   affected independent release. Inspect package contents and compare its
   unpacked result to the declared source. Keep private connection maps,
   environment-specific inputs and package bindings out of public source.
4. **Plan and deploy:** export/retain the target baseline, apply the operation
   to the exact selected environment using qualified CLI commands, and record
   the command result. Avoid broad environment discovery, automatic activation
   or blind retries after uncertain saves.
5. **Read back:** query the exact solution version, components, dependencies,
   environment-variable definitions/current values, connection references and
   companion-resource identities. Compare them with the intended package and
   deployment profile. A successful command is not native readback.
6. **Rehearse recovery:** repeat the dry-run for an already-present release,
   check restricted access without widening it, and document a versioned
   rollback/forward-repair procedure. Preserve in-flight work and owner-managed
   state.
7. **Separate runtime acceptance:** only after explicit deployment/run authority,
   verify behavior with bounded fictional data, actual output and failure
   recovery. Solution presence and source checks are not runtime or operational
   acceptance. Pilot/activation remains a separately authorized decision.

The present design has not performed a native read, package, deployment, run,
activation or permission change. Exact native rights and companion-resource
availability remain environment-specific qualification items.
