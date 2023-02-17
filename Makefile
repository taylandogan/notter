PACKAGE_NAME:=notter
PACKAGE_LOC:=src/$(PACKAGE_NAME)
PYTHON:=python3.10
VENV:=./venv
PIP_VENV:=$(VENV)/bin/pip

.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install -e .

.PHONY: venv_dev
venv_dev:
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install -e '.[dev]'

.PHONY: clean
clean:
	rm -rf $(VENV)
	find $(PACKAGE_LOC) -type d -name __pycache__ -exec rm -r {} \+
	rm -rf *.egg-info build dist
	rm -rf '.mypy_cache'
	rm -rf '.eggs'

.PHONY: format
format: $(VENV_DEV)
	isort $(PACKAGE_LOC)
	black $(PACKAGE_LOC)

.PHONY: lint
lint: format
	black --diff --check $(PACKAGE_LOC)
	flake8 $(PACKAGE_LOC)
	mypy $(PACKAGE_LOC)
	isort --diff --check $(PACKAGE_LOC)

