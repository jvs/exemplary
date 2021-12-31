PYTHON := .venv/bin/python

# Remove random debris left around by python, pytest, and coverage.
clean:
	@echo "Removing generated files."
	@rm -rf \
		__pycache__ \
		.coverage \
		.pytest_cache \
		**/__pycache__ \
		**/*.pyc \
		docs/_build/* \
		dist \
		htmlcov \
		MANIFEST \
		*.egg-info

test: clean exemplary/parser.py
	$(PYTHON) -m pytest -v -s tests.py

exemplary/parser.py: venv grammar.txt generate_parser.py
	$(PYTHON) generate_parser.py

venv: .venv/bin/activate

.venv/bin/activate: requirements.txt requirements-dev.txt
	test -d .venv || python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -r requirements-dev.txt
	touch .venv/bin/activate

# Run the tests, compute test coverage, and open the coverage report.
coverage: clean venv exemplary/parser.py
	.venv/bin/coverage run -m pytest -v -s tests.py
	.venv/bin/coverage report --omit='exemplary/parser.py'
	.venv/bin/coverage html --omit='exemplary/parser.py'
	open "htmlcov/index.html"

# How to publish a release:
# - Update __version__ in exemplary/__init__.py.
# - Commit / merge to "main" branch.
# - Run:
#   - make tag
#   - make upload_test
#   - make upload_real

tag: clean
	$(eval VERSION=$(shell sed -n -E \
		"s/^__version__ = [\'\"]([^\'\"]+)[\'\"]$$/\1/p" \
		exemplary/__init__.py))
	@echo Tagging version $(VERSION)
	git tag -a $(VERSION) -m "Version $(VERSION)"
	git push origin $(VERSION)

# Build the distribution.
dist: clean venv exemplary/parser.py
	rm -rf dist/
	$(PYTHON) setup.py sdist
	.venv/bin/twine check dist/*

# Upload the library to pypitest.
upload_test: dist
	.venv/bin/twine upload --repository pypitest dist/*

# Upload the library to pypi.
upload_real: dist
	.venv/bin/twine upload --repository pypi dist/*

.PHONY: bash clean coverage dist tag test upload_real upload_test
