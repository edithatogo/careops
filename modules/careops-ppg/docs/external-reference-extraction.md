# Retained external-reference extraction

The offline reconciliation CLI can extract literal references for selected
publisher families from hash-verified retained policy bodies. It does not fetch
URLs, choose editions, accept applicability or complete relationship assessments.

The default remains NSQHS names and Commission URLs. To inspect the supported
publisher hosts instead, use the qualified
repository-local Python 3.15.1 external-catalogue profile:

```sh
.venv/bin/python -m scripts.ppg_external_reconciliation \
  --bundle .local/external-bundle.json --local-inputs .local/retained-sources.json \
  --source-root .local/approved-sources --capture-root .local/captures \
  --publisher-host publisher.example.org \
  --publisher-host regulator.example.org \
  --no-nsqhs-names --output-dir .local/new-reference-scope
```

Install the existing hash-locked external-catalogue dependencies in the selected
profile. Inputs follow the maintained catalogue/source contract: each source pins
its document UID, original and extraction paths and SHA256 hashes, retained
version, identity qualification and extraction/conflict state. The source root
bounds the files this invocation may read. Output is create-only and private.

Choose already-qualified publisher hosts explicitly; the example hosts above
are fictional. Host syntax validation does not establish publisher authority.
Other issuers, intranet origins,
redirect destinations and superficially similar domains are not included. HTTP
links can be retained as literal historical evidence; this authorises no request.
Malformed ports and credential-bearing URLs are excluded from retrieval leads.

Each occurrence retains its own offset, page, line, source hashes and context.
Repeated citations remain distinct occurrences. Only an exact URL assertion in
the supplied publication catalogue produces a publication candidate; multiple
assertions stay ambiguous and missing matches stay unresolved. No occurrence
establishes an edition. Hash/identity/extraction holds and identities with no
qualified retained source remain visible in the coverage ledger.

The representation inventory is a separate check of supplied captured HTML.
Neither output proves full bibliographic coverage or acquisition completeness.
Use the installation's existing guarded writer and exact source bindings for
native persistence. Preserve earlier records and protected no-retrieval decisions;
verify the selected delta once and require zero-create unchanged replay.

## Originals retained inside ZIP capsules

An independently qualified historical document identity can use
`identityState: verified_source_identity` with an `originalCapsule` object
containing its private `path`, SHA256 `sha256`, and exact original `member` name.
The extractor verifies the container hash and a single matching member whose
bytes equal the separately pinned original. Missing, changed, malformed or
ambiguous capsules stay held; the original/text hash checks still apply.
The CLI source-root boundary also applies to capsule reads. Nothing is extracted
to disk and no URL is fetched.

Occurrences retain `sourceIdentityState`, `originalCapsuleSHA256` and
`originalCapsuleMember` beside the original/text hashes and offsets. Preserve
those fields when preparing native records. This supports literal-reference
evidence from historical or working sources; it does not establish the requested
edition, publication, applicability, original-reader rendering fidelity or current
authority. Keep those uncertainties explicit.

## PDF links omitted from body text

Some retained PDFs store publisher links in URI annotations. Inspect the verified
original with `pdfinfo -url` from the existing Poppler CLI. Retain its complete
output privately with the original SHA256. This requires no publisher request.

`pdf_uri_inspection(annotation_output, original_sha256)` converts that dump into a
hashable annotation representation. It preserves physical page numbers, repeated
URI occurrences and the raw dump hash. Unsupported/malformed URI values are
recorded separately; unsupported dump rows require reconciliation. This function
does not execute the CLI, retrieve links, review the policy body or prove an
edition. The caller must verify the original bytes and bind the dump to that file.

An explicit `decode_url_wrappers=True` also records the single encoded `url`
parameter of a supported HTTPS redirect wrapper. The original wrapper is retained;
no redirect is followed and its target remains an unverified identity pointer.

Keep the returned inspection text as a new private representation, rather than
replacing the body extraction. Bind its text path/hash, `inspectionKind` and
`annotationOutputSHA256` in the source record before passing it to
`reference_scope`. Use `include_nsqhs_names=False` for this URL-only pass and
select the already-qualified publisher hosts. Native reference data must retain
the annotation representation and raw-dump hash alongside source/offset provenance.
Missing annotations do not establish an absence of references in the policy body.

Supply the complete validated publication/edition/capture records when reconciling
URLs. An exact URL belonging to a retained capture or edition can identify its
parent publication, provided that publication is present in the supplied catalogue.
The result records the matching catalogue keys. It still does not establish the
edition cited by a policy: a publisher can replace content at the same URL.

For a compact review list, `group_pdf_uri_occurrences(scope)` (CLI:
`--group-pdf-uris`) groups the same URI within one retained source representation.
It retains every original occurrence key, page, line and offset in
`annotationOccurrences`. Group counts and physical annotation counts are separate.
Different artifacts, extraction hashes, source identities or inconsistent
resolutions are never combined. Keep existing native reference identities; a
previously saved atomic reference is sufficient only for its own recorded span.

When table columns separate a displayed link's words, inspect its actual PDF
link labels rather than joining unrelated body-text columns:

```sh
.venv/bin/python -m scripts.ppg_external_reconciliation pdf-link-labels \
  --original .local/source.pdf --original-sha256 EXPECTED_SHA256 \
  --page 13 --output .local/link-labels.json
```

The CLI requires installed Poppler `pdftohtml`, verifies the original hash and
processes an immutable private copy of one selected page. Output is create-only
and owner-readable. It retains each anchor label, URL and text box separately,
including repeated targets; it does not infer how fragments should be joined.
The pure parser's `originalBindingVerified` stays false until the CLI binds the
actual processor output. Neither route fetches linked resources, changes native
records, replaces the body extraction or establishes editions/full-body review.
