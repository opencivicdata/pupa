#!/bin/sh
export PYTHONPATH=.
pytest -vvv --cov pupa --cov-report html --ds=pupa.tests.django_settings pupa/tests
