# Assessment history storage

Use `scripts/ppg_assessment_history_archive.py` when repeated reviewed amendments make an assessment manifest too large for a native update. The helper is offline and never authenticates, uploads, changes an assessment state or accepts clinical content.

1. Read the exact current assessment and retain its ETag and manifest SHA-256.
2. Choose a new hash-addressed file in the existing private evidence library. Call `prepare_archive(manifest, archive_url)`.
3. Qualify the exact destination and its write effects through the existing CLI route. Upload `archive_bytes` with overwrite disabled. Read the saved bytes back and require exact SHA-256 parity before updating the assessment.
4. Conditionally save only `EvidenceManifest=compacted_manifest` against the original ETag. Reconcile an uncertain upload or update by exact readback before another attempt.
5. Verify the original completion, sources and other fields are unchanged. `restore_original(compacted_manifest, archive_bytes)` must reconstruct the exact original manifest, including every prior amendment and inventory entry. An unchanged compaction replay returns no plan.

The current manifest retains the latest amendment and inventory record and a URL/hash/count reference to the immutable history file. Existing archive references form a chain. Keep all archive files and include them in recovery exports; the current list row alone is not the full history. Later amendments append normally. Verify each compaction before further updates, because reconstruction validates that exact compaction checkpoint.

Keep native URLs, operational archives, tenant bindings and receipts private. Source and tests use fictional inputs only. This helper does not resolve document editions, owner decisions or publisher limitations.
