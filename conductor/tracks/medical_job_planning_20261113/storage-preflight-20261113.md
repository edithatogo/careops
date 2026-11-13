# Medical Job Planning — read-only physical layout preflight (source slice)

**Status:** source-development candidate (13 November 2026). **Not an approved native SharePoint site, role, tenant, provisioned List, data migration, industrial rule, records policy or production readiness claim.**

## Objective

Validate the **structure** of an independently authorised future SharePoint readback against the exact 20-List/one-Library logical inventory extracted from the user-supplied v0.4.2 prototype. Make dangerous drift conspicuous before any native authoring or migration work, without introducing a write route or installing all proposed Lists.

## Implemented source

- `modules/careops-medical-job-planning/storage-contract.json` now records each of the prototype's 20 Lists with its `Key`, exact 0.4.2 proposed internal fields, logical security cohort and source SHA-256 of `config/data-model.json`. The `Payload` column represents **development-only generic JSON**; production field size/index/schema must be independently qualified.
- `storage_preflight.py` is a **pure offline comparator**. It checks collection names (including case collisions), field presence, key uniqueness, missing objects, undocumented additional objects, and permission-scope growth (5,000 is a **review threshold**, not a guarantee of security). It rejects malformed readbacks.
- It returns `structural_match_only` on apparently matching data and **always** returns `permission_qualified=false`, `native_source_authenticity_qualified=false`, `provisioning_authorised=false` and `write_operations=[]`.
- `tests/test_mjp_storage_preflight.py` exercises structurally complete fictional readback, missing lists/libraries, missing columns, uniqueness failure, excessive scopes, extra objects, duplicate/ambiguous readback and fail-closed no-write outcomes. `tests/test_mjp_storage_contract.py` now asserts all 20 exact source-field inventories.
- Source is wired into exact Python 3.15.1 module CI and public-source inventory.

## Not yet completed

W-1 **MJP-P03** actual storage decision, W1 MJP-103 physical layout, and W2 MJP-201–203 tenant capability, native privileges, idempotent approved provisioning and physical ACL tests remain **OPEN**. The comparator has **no network** and cannot verify actual SharePoint internal names, Microsoft Graph/Power Platform licences, site permissions, delegated approval rights, DLP, concurrency, versions, retention, document exports, source authenticity, small-cell disclosure or a real restoration. An authorised owner must supply and review actual readback privately before any native change.

Do not optimise for a cosmetic green preflight by creating phantom Lists or broadening access. Structural matches are not operational go-live approvals. Existing Workforce BI private data feeds and source ownership remain untouched.
