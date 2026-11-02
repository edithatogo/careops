# Register policies maintained outside the source workbook

Use a private version-1 JSON manifest to register each existing catalogue item. Populate its documentUID, numeric itemId, printedIdentifier and evidenceRef from the live record. Keep the populated manifest with the installation. The portable workflow starts with an empty manifest.

Run the following with the repository-local interpreter against an exported QW3 definition and a new output path.

    .venv/bin/python scripts/ppg_registry_only.py definition.json private-manifest.json candidate.json

Keep the accepted definition and checkpoint for recovery. Compare the candidate with the export before deployment. Verify workbook-managed, retained-absent and Registry-only counts separately. Open the linked files and compare their hashes. Exercise reconciliation again with identical source bytes and verify zero attempted catalogue writes.

When a workbook later gains a registered policy, use the existing reviewed identity application to authorise its existing UID for workbook management. Verify the same catalogue item and its editions after the first update and after replay. Unknown identities require a decision.
