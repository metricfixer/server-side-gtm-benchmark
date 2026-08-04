PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python

.PHONY: install browser smoke benchmark verify test checksums assets release clean

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.lock.txt

browser:
	$(VENV_PYTHON) -m playwright install chromium

smoke:
	$(VENV_PYTHON) src/run_benchmark.py --runs-per-variant 1 --output-dir artifacts/smoke

benchmark:
	$(VENV_PYTHON) src/run_benchmark.py --output-dir artifacts/full-run

verify:
	$(VENV_PYTHON) scripts/verify_results.py
	$(VENV_PYTHON) scripts/verify_checksums.py

checksums:
	$(VENV_PYTHON) scripts/generate_checksums.py

test:
	$(VENV_PYTHON) -m unittest discover -s tests -v

assets:
	$(VENV_PYTHON) scripts/generate_assets.py

release: verify test assets
	$(VENV_PYTHON) scripts/build_release.py

clean:
	rm -rf artifacts build .pytest_cache __pycache__ src/__pycache__ scripts/__pycache__ tests/__pycache__
