# Test repeat deployment on a populated Registry

Use an isolated workbench, a fictional Catalogue record and two distinguishable fictional DOCX files. Create two revisions using **Upload updated PPG** on that record. Verify that **Open linked files** opens each working document and that each revision has a distinct submitted Review Queue case. Compare the original attachments with the source documents byte for byte.

1. Capture a private baseline. Record the linked files' IDs, versions and hashes, and the cases' IDs, versions, status, draft links and attachment hashes. Include an unrelated case if you want to check queue-wide preservation.
2. Set `preservationRecordId` to the fictional record ID in your private settings. Run the [deployment command](registry-upload-cli.md). Inspect the receipt for the expected configuration changes and a successful preservation comparison.
3. Run the identical command again. Require zero writes, the same preservation digest and the same edition and case IDs. Reopen both files from the original record, follow each case link and compare the earlier edition with the baseline.
4. Store run-specific receipts and digests outside Git.

This procedure passed on a populated isolated installation. The non-owner production acceptance test remains open until staff submit an actual revision.
