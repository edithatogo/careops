# Deploy the Registry upload action

From a checkout containing this extension, run:

```sh
node scripts/ppg_registry_upload.mjs /absolute/path/to/private/registry-upload.json
```

Run the **same command again** to verify the installation. Matching components are read back without writes. Append `--verify-only` to require an existing deployment and refuse changes. Success prints the write count and a path to the private verification receipt. A nonzero exit means verification did not complete.

## Set up the destination once

Use an existing same-tenant PPG workbench. Copy [the settings example](../config/registry-upload.example.json) outside Git and replace the example values. Supply the exact Catalogue, Review Queue and versioned evidence library GUIDs and the enrolled SharePoint connector connection name. Queue attachments must be enabled. The command reads folder paths from the lists. For an existing flow supply its exact `flowId`. Without it, the command discovers a unique exact display name and creates the flow when absent.

Point `binding` to the private binding for the currently selected Microsoft 365 CLI Toolkit login. It contains `siteUrl`, `sdkDirectory` (the installed CLI dist directory), `connectionName` (saved CLI login, distinct from the connector connection name), and `identity` with `tenantId`, `appId`, `objectId` and `username`. Use the already enrolled operator and the Default environment of that tenant. Paths for the binding and receipts are relative to the settings file. Use one stable, private receipt directory per destination. There is no password or token in the settings.

## What the command installs and verifies

It checks the destination lists and adds the review submission folder, case key, capture classification and linked-files view. It deploys the selected-record flow, checks its definition and caller-provided SharePoint connection, starts it, sets Catalogue run-only access, and checks the button, view and record footer. The caller needs existing access to submit to the Review Queue and evidence library. The action accepts a PDF or DOCX and a revision label. Use a short revision label such as `3.1 draft 2`. The deployed workflow accepts up to 52 characters, but the default queue key also limits the lowercased label to 105 UTF-8 bytes. Longer multibyte labels can fail at case creation. Each distinct revision creates a review case with the original attachment and a separate working copy. Replaying the same revision and contents reuses the case. Conflicting content or configuration stops the operation.

For a populated, already installed Registry, set `preservationRecordId` to the numeric ID of a representative record that has linked files and review cases. The same command then reads the record's file view and cases before and after deployment, downloads and hashes files and attachments, and checks versions, identifiers and case fields. Omit this option on an installation without an existing populated record. A deployment without this option verifies configuration only.

Changes that replace shared capture choices or the record footer require a native version token. If the server omits it, apply that setting in SharePoint and rerun the installer. Native writes use a local intent journal and a single writer lock. A transport failure can leave `pending.json`. Inspect the named resource and reconcile its actual state before archiving that journal and rerunning. If a process ended unexpectedly, confirm its PID has exited before removing its stale lock. Never remove another operator's active lock. Retain the receipts privately.

## Acceptance

Production **non-owner submission is open** until staff submit an actual revision from the appropriate production record. Before submission, capture the earlier edition's ID, version and hash. After submission, follow **Open linked files** from that record, verify the new file opens and has its own submitted Review Queue case, and compare the earlier edition to its baseline. Neither configuration verification nor repeating the installer submits a PPG.

See the [repeat deployment test](registry-upload-repeat.md) for the populated-installation procedure.
