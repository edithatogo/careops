# Workforce dashboard source

Open Workforce.pbip in Power BI Desktop. The project contains the report pages and model definitions. Blank source parameters select header-only feeds and the report opens against its colocated semantic model. Historical period anchors in calculations are business rules inherited from the qualified dashboard.

## Release workflow

1. Review PBIR and TMDL changes in a pull request. Review all changed text and regenerate source-lock.json from the sorted path-to-SHA256 inventory in alm.py. Run `python alm.py` on Python 3.15.1 and validate PBIR and TMDL before tagging the reviewed revision.
2. Keep the source snapshot and deployment configuration in the private deployment lane. Supply all 66 gzip CSV feeds listed in feed-schema.json. For the nine formerly embedded feeds, materialise the original gzip bytes in private storage under the corresponding embedded filenames.
3. Run `python alm.py --bind PRIVATE_CONFIG PRIVATE_FEEDS NEW_PRIVATE_BUILD`. The JSON configuration requires stage, source_site, source_folder and sha256. The last field maps each feed filename to its approved SHA256. Stage is development, test or production. The command checks each feed header and digest and materialises the environment parameters only in the private build.
4. Deploy the same reviewed source revision to the approved development workspace through the existing guarded Fabric definition route or the organisation’s PBIP deployment tooling. Bind the report to that environment’s model and configure the existing authorised cloud connection. Record commit, stage, item identities, source manifest and terminal refresh. Verify model and report readback and reconcile row counts, measures and visuals before promoting to test and production. Each stage uses its own private binding and explicit promotion decision.
5. Recover by selecting the previous approved source revision and private snapshot, then repeat binding, deployment, refresh and readback. Keep receipts and exported data in private storage.

The public check guards the reviewed file inventory. Review any proposed lock change alongside its source diff. The public workflow performs source verification. Native deployments and environment approvals are handled in the private release lane.
