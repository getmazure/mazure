SHELL := /bin/bash

init:
	@pip install -e .
	@pip install -r requirements-dev.txt

lint:
	@echo "Running ruff..."
	ruff check mazure tests
	@echo "Running black... "
	$(eval black_version := $(shell grep "^black==" requirements-dev.txt | sed "s/black==//"))
	@echo "(Make sure you have black-$(black_version) installed, as other versions will produce different results)"
	black --check mazure/ tests/
	@echo "Running pylint..."
	pylint mazure tests
	@echo "Running MyPy..."
	mypy --install-types --non-interactive
