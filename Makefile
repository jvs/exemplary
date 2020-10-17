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
	-rm -rf \
		__pycache__ \
		.coverage \
		.pytest_cache \
		**/__pycache__ \
		**/*.pyc \
		docs/_build/* \
		dist \
		htmlcov \
		MANIFEST

# Run the tests in a docker container.
test: clean image
	$(RUN) python -m pytest -v -s tests.py

# Run the tests, compute test coverage, and open the coverage report.
coverage: clean image
	$(RUN) /bin/bash -c "coverage run -m pytest -v -s tests.py \
		&& coverage report \
		&& coverage html"
	open "htmlcov/index.html"

# Build the distributeion.
dist:
	rm -rf dist/
	python3 setup.py sdist
	twine check dist/*

# Upload the library to pypitest.
test_upload: dist
	twine upload --repository pypitest dist/*

# Upload the library to pypi.
real_upload: dist
	twine upload --repository pypi dist/*

.PHONY: clean test coverage dist test_upload real_upload bash
