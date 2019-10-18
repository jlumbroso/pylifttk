# Makefile for the 'pylifftk' package.
#
# Author: lumbroso@cs.princeton.edu
# Last Change: October 17, 2019
# URL:
#
# Note: This Makefile was designed by originally designed for the
# 'humanfriendly' package by Peter Odding <peter@peterodding.com>
# under MIT license.
#
# https://raw.githubusercontent.com/xolox/python-humanfriendly/0e0c80cc7b5d6c29deae3ad589928102e421cb2f/Makefile


PACKAGE_NAME = codepost
WORKON_HOME ?= $(HOME)/.virtualenvs
VIRTUAL_ENV ?= $(WORKON_HOME)/$(PACKAGE_NAME)
PATH := $(VIRTUAL_ENV)/bin:$(PATH)
MAKE := $(MAKE) --no-print-directory
SHELL = bash

ci:
	pipenv run pytest --cov=codepost

init:
	pip install --upgrade pip~=18.0 pipenv==2018.10.13
	pipenv install --dev --skip-lock

coveralls:
	pipenv run coveralls

test:
	pipenv run tox -p auto

default:
	@echo "Makefile for $(PACKAGE_NAME)"
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make install    install the package in a virtual environment'
	@echo '    make reset      recreate the virtual environment'
	@echo '    make check      check coding style (PEP-8, PEP-257)'
	# @echo '    make test       run the test suite, report coverage'
	# @echo '    make tox        run the tests on all Python versions'
	# @echo '    make readme     update usage in readme'
	# @echo '    make docs       update documentation using Sphinx'
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo '    make clean      cleanup all temporary files'
	@echo

install:
	@test -d "$(VIRTUAL_ENV)" || mkdir -p "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/python" || virtualenv --quiet "$(VIRTUAL_ENV)"
	@test -x "$(VIRTUAL_ENV)/bin/pip" || easy_install pip
	@pip uninstall --yes $(PACKAGE_NAME) &>/dev/null || true
	@pip install --quiet --no-deps --ignore-installed .

reset:
	$(MAKE) clean
	rm -Rf "$(VIRTUAL_ENV)"
	$(MAKE) install

check: install
	@pip install --quiet "flake8>=2.6.0" "flake8-docstrings>=0.2.8" "pyflakes>=1.2.3"
	@flake8

# test: install
# 	@pip install --quiet --constraint=constraints.txt --requirement=requirements-tests.txt
# 	@py.test --cov
# 	@coverage combine || true
# 	@coverage html

# tox: install
# 	@pip install --quiet tox
# 	@tox

# readme: install
# 	@pip install --quiet cogapp
# 	@cog.py -r README.rst

# docs: readme
# 	@pip install --quiet sphinx
# 	@cd docs && sphinx-build -nb html -d build/doctrees . build/html

publish: install
	git push origin && git push --tags origin
	$(MAKE) clean
	pip install --quiet twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*
	$(MAKE) clean

clean:
	@rm -Rf *.egg *.egg-info .cache .coverage .tox build dist docs/build htmlcov
	@find . -depth -type d -name __pycache__ -exec rm -Rf {} \;
	@find . -type d -name '.pytest_cache' | xargs rm -Rf
	@find . -type f -name '*.pyc' -delete

.PHONY: default install reset check publish clean # test tox readme docs