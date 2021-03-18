#!/bin/sh
pytest --cov pupa --cov-report html --ds=pupa.tests.django_settings
