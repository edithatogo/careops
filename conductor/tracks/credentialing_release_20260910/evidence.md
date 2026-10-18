# Evidence: credentialing MVP source-contract release

Observed 10 September 2026.

## Merged source components

| Component | Commit | Evidence scope |
|---|---|---|
| Policy Atlas credentialing collection | `c7fd8b8835034280badde76cfd8765b018c9abd5` | Public-source metadata, 88-entry model catalogue, Rural Generalist source-currentness controls and public-safe dataset build |
| CareOps parent control plane | `7ea09a387eaa19b43787a07f2df5cd9cb1d35933` | Generic modular architecture, authority profile, initial compatibility and validation |
| CareOps Approve | `ec7d7230b0fae3293c7ed51e716074074f83b5bb` | Intake, reconciliation, versioned handoff, human review and negative paths |
| CareOps Decisions | `69aa4e5a1d0851feb0d75900f0dabc618544e66c` | Committee recommendation, separate delegated decision, procedural fairness and process maps |
| CareOps Process | `e31bdd9213178e7996d4bdb6685bba8d83be22f8` | Strict privacy-minimised event validation, replay safety and aggregate assurance |
| CareOps Legacy Migration | `7316a757028fb44e8f77b35ca14f7b426e2527db` | API-first and controlled HTML read adapters, source provenance and synthetic tests |
| CareOps Incidents | `78e297335a95728f13a8f84b9b20e4f523d1128f` | Later, disabled safety-signal design boundary |
| CareOps Finance | `5fcdd09af6871d895f1adc245ab245357edafaf2` | Generic reporting, RLS, reconciliation and ALM patterns |

CareOps Costing remains a draft design at `b30e2a55c0d4274d88a5aa1d56796500cfd09f42` and is not included as a released implementation dependency.

## Validation observed before merge

- Policy Atlas strict Python, adversarial, security, context, dependency and source-staging workflows passed.
- CareOps parent Python 3.14 credentialing contracts, portfolio validation and harness gate passed.
- CareOps Approve credentialing contracts, repository validation, package validation, secret scan and harness gate passed.
- CareOps Decisions credentialing contracts, repository validation, packaging and process-model checks passed.
- CareOps Process Python 3.14 CI, secret scan and workflow-security checks passed.
- Legacy Migration source-adapter and harness workflows passed.
- Incidents publication-boundary validation passed.
- Finance validation, evidence-hardening and CodeQL workflows passed.

## Parent release evidence

- `portfolio/credentialing-mvp-compatibility.json` records immutable component commits and status boundaries.
- `portfolio/credentialing-contract-matrix.json` records the versioned interfaces.
- `portfolio/credentialing-authority-profile.example.json` pins the Policy Atlas collection while remaining design-only.
- `portfolio/releases/credentialing-mvp-0.1.json` records the source release and exclusions.
- The parent `careops-approve` gitlink is pinned to `ec7d7230b0fae3293c7ed51e716074074f83b5bb` in this branch.

## Evidence ceiling

The evidence proves source-control integration and synthetic contract behaviour. It does not prove current CHHHS authority, complete source data, Microsoft tenant deployment, live-system access, workflow usability, benefit, policy compliance or operating effectiveness.
