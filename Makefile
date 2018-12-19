requirements: requirements-dev.txt requirements.txt

install:
	pip-sync requirements-dev.txt requirements.txt


requirements-dev.txt: requirements-dev.in
	pip-compile --output-file $@ $<

requirements.txt: requirements.in setup.py
	pip-compile --output-file $@ $<


.PHONY: requirements install
