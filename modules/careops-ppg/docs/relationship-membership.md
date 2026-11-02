# Keep relationship assessment membership current

After adding catalogue identities, export the catalogue, assessment register and
relationship register through the installation's qualified CLI client. Use paged
reads from the same site and retain exact preimages privately.

```sh
.venv/bin/python scripts/ppg_relationship_membership.py .local/catalogue.json .local/assessments.json .local/relationships.json .local/membership-plan.json --membership .local/source-membership.json
```

The command prepares only missing progress rows. It preserves completed reviews,
human fields and records outside the current catalogue. Identity changes become
explicit conflicts; do not apply a conflicted plan without reconciliation.

Apply the creates through the existing qualified SharePoint batch route, at most
20 operations per batch. Verify add permission, versioning and unique assessment
keys first. Journal before sending, inspect every operation result and read back
the complete expected fields. Reconcile uncertain writes before resuming; never
blindly retry a batch. Re-export and require zero creates on unchanged replay.

New rows are **Needs relationship review**, with zero qualified sources and no
authority assertion. They require full-source and endpoint review before an
assessment can be completed. This membership reconciliation does not resolve
edition conflicts, clinical applicability or publisher-access limitations.

The membership file maps each new UID to the qualified active or retained source
classification. Catalogue presence alone is insufficient; missing membership
evidence produces a conflict. Keep the source checkpoint proving the mapping.

## Recovered evidence and documentary proposals

A recovered body can move an assessment from **Needs evidence** to **Needs
relationship review** after its document identity, original/native byte hashes
and complete extraction are qualified. Preserve earlier evidence and distinguish
the retained edition from the register edition. This transition does not complete
the substantive assessment or establish current approval.

Keep documentary-reference proposals in **Proposed**. Pin both retained endpoint
artifacts and the literal source passage. Missing exact cited-edition evidence,
identity conflicts and reference-scope holds remain explicit. A documentary
reference does not establish an operative dependency or clinical applicability.

After adding relationships, refresh the existing incoming/outgoing counts and key
inventories without changing assessment conclusions or human decisions. Keep a
dated completion's original comparison scope intact; newer inventory is separate
evidence for subsequent review.

For conditional updates inside a SharePoint batch, reuse the `MERGE` request-line
pattern in [the dataset refresh builder](../scripts/ppg_dataset_refresh.py), with
each item's exact `IF-MATCH` ETag. The outer request is `POST` to `$batch`. Bound
each batch to 20 operations, retain the raw per-operation response before parsing,
and verify every changed row. Reconcile an uncertain batch by exact readback
before another send; do not repeat successful writes. Qualify the changed route
on one selected operation before expanding to the batch.
