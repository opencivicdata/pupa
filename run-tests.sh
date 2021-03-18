#!/bin/sh
EXPORT PYTHON_PATH=.
pytest --cov pupa --cov-report html --ds=pupa.tests.django_settings
