PACKAGE_NAME:=notter
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
	find $(PACKAGE_NAME) -type d -name __pycache__ -exec rm -r {} \+
	rm -rf *.egg-info build dist
	rm -rf '.mypy_cache'
	rm -rf '.eggs'

.PHONY: format
format: $(VENV_DEV)
	isort $(PACKAGE_NAME)
	black $(PACKAGE_NAME)

.PHONY: lint
lint: format
	flake8 $(PACKAGE_NAME)
	mypy $(PACKAGE_NAME)
	isort --diff --check $(PACKAGE_NAME)
	black --diff --check $(PACKAGE_NAME)