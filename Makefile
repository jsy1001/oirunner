.PHONY: requirements update-deps install pip-tools touch

PREREQS = requirements-dev.in pyproject.toml
TARGETS = requirements-dev.txt requirements.txt

requirements: pip-tools $(TARGETS)

update-deps: pip-tools touch $(TARGETS)

install: pip-tools $(TARGETS)
	pip-sync $(TARGETS)
	rm -rf .tox

pip-tools:
	pip install --upgrade pip-tools pip setuptools

touch:
	touch $(PREREQS)

requirements-dev.txt: requirements-dev.in requirements.txt
requirements.txt: pyproject.toml

$(TARGETS):
	pip-compile --upgrade --build-isolation --resolver=backtracking --output-file $@ $<
	touch $@
