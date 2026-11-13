# Fractional portfolio diversity — bounded implementation contract

**Population:** title-keyword-classified publications with nonempty canonical key and RIMS source status `Included`. Source label is **not** independent institutional attribution.

## MoSCoW

- **Must**: represent source population, period years, classifiable denominator, unclassified titles, overlapping topic assignments, zero/empty cases and deterministic output.
- **Must**: allocate each classified paper exactly one total unit, divided equally among its 1..N unique topic labels, then compute Shannon entropy in bits and effective number of themes `2**H`.
- **Must**: reject blank/duplicate labels; document that entropy is conditional on classified titles and should not be interpreted as externally validated disciplinary diversity.
- **Must**: red/green focused tests and source-only CI; preserve original private RIMS register outside public Git.
- **Should**: report changed classification coverage between historical periods and compare with OpenAlex taxonomy after external validation.
- **Could**: move reusable pure functions to CiteLattice once contracts are accepted.
- **Won't**: infer clinical research quality, researcher ranking, clinical value or automatic CHHHS adjudication.

## Acceptance

Six deterministic synthetic tests cover fractional allocation, duplicates, unclassified titles, invariance, and temporal denominator disclosure; hosted checks and independent source review recorded before archive.
