# Runs the docker container and executes the command.
RUN := docker run --rm --name exemplary -v `pwd`:/workspace exemplary

# Runs bash in the container.
bash:
	docker run --rm --name exemplary -v `pwd`:/workspace -it exemplary /bin/bash

# Create a docker image with Python and our dev dependencies.
image: Dockerfile
	docker build -t exemplary .

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

parser: grammar.txt
	$(RUN) python generate_parser.py

# Run the tests in a docker container.
test: clean image parser
	$(RUN) python -m pytest -v -s tests.py

# Run the tests, compute test coverage, and open the coverage report.
coverage: clean image
	$(RUN) /bin/bash -c "coverage run -m pytest -v -s tests.py \
		&& coverage report --omit='exemplary/parser.py' \
		&& coverage html --omit='exemplary/parser.py' "
	open "htmlcov/index.html"

# How to publish a release:
# - Update __version__ in exemplary.py.
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
dist: clean parser
	rm -rf dist/
	python3 setup.py sdist
	twine check dist/*

# Upload the library to pypitest.
upload_test: dist
	twine upload --repository pypitest dist/*

# Upload the library to pypi.
upload_real: dist
	twine upload --repository pypi dist/*

.PHONY: bash clean coverage dist tag test upload_real upload_test
