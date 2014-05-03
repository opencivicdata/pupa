# Pupa: A legislative data scraping framework

[![Build Status](https://travis-ci.org/opencivicdata/pupa.svg?branch=master)](https://travis-ci.org/opencivicdata/pupa)
[![Coverage Status](https://coveralls.io/repos/opencivicdata/pupa/badge.png?branch=master)](https://coveralls.io/r/opencivicdata/pupa?branch=master)
[![Latest Version](https://pypip.in/version/pupa/badge.png)](https://pypi.python.org/pypi/pupa/)
[![Download Format](https://pypip.in/format/pupa/badge.png)](https://pypi.python.org/pypi/pupa/)


The latest stable version of pupa is 0.3.0, which can be obtained via ``pip install pupa`` or by grabbing the tag 0.3.0.

The master branch is in an experimental state at the moment, and usage is not recommended.

## Popolo

Pupa implements the Person, Organization, Membership and Post models from the [Popolo data specification](http://popoloproject.com/). Notably, it:

* does not implement an `id` property, instead using `_id` from MongoDB, with the exception of the `id` property on the Post model
* does not implement [name components](http://popoloproject.com/specs/person/name-component.html) on the Person model
* does not implement a top-level `email` property on the Person model, instead using the `contact_details` property for all contact information
* does not implement a `sources` property on the Membership model
* does not implement `created_at`, `updated_at` or `sources` properties on the Post model
* requires the `name` property on the Person and Organization models, and the `label` property on the Post model
* does not implement [embedded JSON documents](http://popoloproject.com/specs/#embedded-json-documents), with the exception of the `posts` property on the Organization model
