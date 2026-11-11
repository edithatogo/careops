# Technology stack

- Current source is the private CareOps repository, with reviewed reusable-source
  boundaries preserved. Most selected modules are ordinary source; the source
  registry and Git tree identify remaining exact-pinned references.
- Default profile: native SharePoint Lists/Libraries, native forms or Microsoft
  Forms, standard Power Automate/Approvals, Basic Planner where selected, maintained
  Word templates and manual editing. No premium or Copilot core dependency.
- Every capability is optional and standalone. Clinical Hub is a logical Decisions
  submodule with an independent package/path. PPG is policy management with optional
  standards/accreditation. Catalogue describes datasets/resources, including registries.
- Exact repo-local Python 3.15.1 and existing hash-locked module runtimes serve
  development, tooling and analysis. No CLI is needed for ordinary operator work.
  PAC, SharePoint administration and source Git have distinct jobs.
- Retain full Dataverse credentialing and other premium implementations as explicitly
  selected profiles. Lists administration does not establish equivalence to the
  authoritative register's security, transaction and recovery contract.
- Versioned reference and file contracts integrate optional modules. Native record
  authority remains local. Archives are read-only snapshots, not editable mirrors.
- GitHub remains the maintained source host. Keep checks portable; a second private
  host or runner needs destination qualification. Hosted refusal is not execution.
- Offline privacy/secrets, source/security/dependency scans and current-head gates
  remain required. No operational data, findings or bindings in Git/artifacts.
- Copilot, AI Builder, local models, advanced search/analytics and unattended desktop
  automation are optional. None is decision authority or a prerequisite to core work.

See [standard suite](../docs/standard-suite.md),
[CLI ownership](../docs/standard-suite.md#cli-ownership-one-tool-per-job),
[native credentialing target](../portfolio/native-credentialing-target.json) and
[source migration](../docs/source-migration-plan.md).
