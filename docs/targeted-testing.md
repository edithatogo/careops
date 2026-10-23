# Targeted testing and reusable results

Use the selected repository-local Python 3.15 interpreter. During edits, run the
smallest meaningful affected tests; reuse unchanged evidence instead of rerunning
the whole suite. Full integration, clean-package, security, native and release
acceptance remain separate requirements. Never describe a selected or empty run
as full-suite verification.

## Pytest development loop

Choose an explicit file, node or expression first:

```sh
.venv/bin/python -m pytest tests/test_example.py::test_retry -q
.venv/bin/python -m pytest tests/test_example.py -k recovery -q
.venv/bin/python -m pytest --last-failed --last-failed-no-failures=none -q
.venv/bin/python -m pytest --failed-first
.venv/bin/python -m pytest --stepwise
```

The first two commands select changed behavior. Failure-only mode deliberately
does nothing if no failure is cached; that is not passing evidence for new code.
Failed-first still runs the entire selected suite. Stepwise is an interactive
debugging loop, not a release gate. On a cold cache, select relevant tests or run
the applicable suite; do not infer that no cached failures means correctness.

Preserve cacheprovider. Cache locally per worktree and selected environment; do
not share writable cache databases across parallel owners. Cache artifacts remain
ignored, private and disposable. Key any CI cache to interpreter, platform,
dependency locks and test configuration. A cache miss must never drop a required
test. Shared fixtures, schemas, generated inputs, dependency/configuration changes
or uncertain impact require the wider affected suite or full baseline.

If global pytest addopts enable whole-suite coverage thresholds, use the qualified
pytest-cov `--no-cov` option for a focused development run. Keep the existing
coverage threshold on full integration runs. A partial coverage result must not
overwrite or be presented as the full coverage baseline.

## Plugins and honest failures

- `pytest-difftest` is optional, not an acceptance gate. Version 0.3.0 has no
  CPython 3.15 wheel; the actual 3.15.1 source build failed because PyO3 0.25.1
  supports only through 3.14. Do not bypass that check or downgrade Python.
  Requalify a maintained upstream fix before adding it to a repository lock.
  Qualification must include new/deleted tests, fixtures, configuration and
  non-Python input changes; compare selection against a clean full baseline.
  Keep baselines local; no S3 or other external storage is configured.
- `pytest-rerunfailures` 16.7 and pytest 9.1.1 install on 3.15.1. Installation
  alone does not qualify a repository. Default to zero reruns. An opt-in retry
  needs an identified transient cause, a small bound and visible original failure.
  Keep flaky outcomes visible (`--fail-on-flaky` where qualified), and never
  replay native mutations, sends or real external operations as a test retry.
- `skip`/`skipif` require an actual capability or platform condition and a reason.
  `xfail` requires a known issue, reason and `strict=True` so an unexpected pass
  is investigated. Neither is a speed optimisation or permission to hide failure.

## Existing native runners

Do not convert a working suite solely to gain pytest flags. Unittest can use
`python -m unittest discover -s tests -p test_selected_module.py -v`. Keep Cargo,
PowerShell, JavaScript and Gradle focused selectors where those are the real
tests. Do not run a Python helper on an older interpreter to select them.

The parent includes `portfolio-scripts/run_tests.py`: focused selectors are
required, failure-only never silently expands to all tests, cache directories
are environment/lock keyed, inherited reruns are disabled, and full modes retain
coverage. Run it from the repository working directory with its own environment:

```sh
.local/ci-latest-3151/bin/python portfolio-scripts/run_tests.py --runner unittest --mode focused --tests-root portfolio-scripts/checks test_test_selection.py
```

Full CI remains the coherent integration/release check. Before merging, verify
all required checks for the exact current head and then main. A selective cache
or plugin cannot substitute for native readback, recovery or operator acceptance.

References: [pytest cache](https://docs.pytest.org/en/stable/how-to/cache.html),
[skip/xfail](https://docs.pytest.org/en/stable/how-to/skipping.html),
[difftest source](https://github.com/PaulM5406/pytest-difftest),
[rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures).
