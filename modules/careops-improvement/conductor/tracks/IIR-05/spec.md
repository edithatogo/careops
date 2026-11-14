# Solution lifecycle and pilot

Proposed / awaiting review. The independent solution and companion resources
are declared in [`config/resources.json`](../../../config/resources.json). The
CLI-only design and native acceptance boundary are in
[`docs/deployment-design.md`](../../../docs/deployment-design.md).

Design an independently versioned Power Platform solution owned by this module.
Define its publisher, solution identity, dependencies, environment variables,
connection references and companion SharePoint and BI artifacts. Specify CLI
bootstrap, upgrade, readback and recovery. No connector definitions or native
bindings are inferred by this portable manifest.
