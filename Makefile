PACKAGE_NAME:=notter
PYTHON:=python3.10

export PYTHONPATH=$(CURDIR)/$(PACKAGE_NAME)


.PHONY: venv
venv:
	$(PYTHON) -m venv venv
	pip install -e .

.PHONY: venv_dev
venv_dev:
	$(PYTHON) -m venv venv
	pip install -e .[dev]

.PHONY: clean
clean:
	rm -rf venv
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