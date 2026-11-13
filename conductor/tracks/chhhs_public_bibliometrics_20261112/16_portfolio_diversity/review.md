# Conductor review — Track 16 (source-only, provisional)

## Scope and observations

Reviewed pure-Python module against bounded specification, six synthetic tests and the private source-labelled aggregate. Code rejects repeated/blank labels, equally weights each classified paper and returns null entropy when no title can be classified. No personal records are exported.

## Findings and repairs

- **Correctness:** balanced fractional assignment prevents publications carrying many labels from dominating entropy. Explicitly excludes unclassified papers from denominator and reports their count.
- **Scientific interpretation:** classification coverage differs (40.0% versus 48.5%). This makes point change from 6.34 to 7.20 sensitive to rulebook and ascertainment; describe as *heuristic*.
- **Testing:** RED import failure and six GREEN synthetic tests observed locally on Python 3.13. Hosted real-data CI and independent external scientific review remain pending.
- **Disposition:** do **not** mark track archived or independently verified yet. Follow-up: OpenAlex topic taxonomy comparison, classification sensitivity and CI.

This is a manual source-review following the upstream `conductor-review` criteria; it is not a claim that Gemini CLI's native Conductor command ran.
