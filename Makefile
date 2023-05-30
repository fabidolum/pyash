# simple makefile
# inspired from https://github.com/python-poetry/poetry/blob/master/Makefile

clean:
	@rm -rf build .eggs *.egg-info
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

black:
	@poetry run black pyash/ tests/ 

format: clean black

tests:
	@poetry run coverage run --source=pyash -m pytest -vv tests/

cover: tests
	@poetry run coverage report -m

version := $(shell poetry version -s)

build:
	@poetry build


.PHONY: tests doc build publish

