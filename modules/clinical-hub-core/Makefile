PYTHON ?= .venv-ci/bin/python
export PATH := $(abspath $(dir $(PYTHON))):$(PATH)
.PHONY: ci test fuzz audit secrets validate
validate:
	$(PYTHON) scripts/validate_public_source.py
test:
	$(PYTHON) -m pytest -q
ci: validate test
fuzz:
	$(PYTHON) -m pytest -q tests/test_calendar_fuzz.py
audit:
	$(PYTHON) -m pip_audit -r requirements-dev.lock
secrets:
	bash scripts/check_secrets.sh staged
	bash scripts/check_secrets.sh history
