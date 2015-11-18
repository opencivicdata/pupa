# pupa changelog

## 0.5.2 -

* show run logs in the admin

## 0.5.1 - November 13 2015

* use other\_names for psuedo\_id resolution on people
* fix for postgis:// on Heroku
* remove dump command that required imago
* require py-ocd-django 0.8.0 models

## 0.5.0 - October 8 2015

* fix major bug causing deadlock on party import
* fix major bug where legislative\_session changes would wipe the database
* update from Django 1.7 to Django 1.9
    * now uses Django's ArrayField, JSONField, etc. instead of external deps
    * also now requires Postgres 9.4
* changes to be consistent with Popolo in naming of legislative\_session and vote\_event
* some speedups on import by changing how we use bulk\_create
* experimental Kafka support
* actually use other\_names for person import
* allow delayed resolution of people
* respect locked\_fields during import
* renamed make\_psuedo\_id() to discourage use
* lots of other bugfixes

## 0.4.1 - August 13 2014

* bugfix release for packaging issue w/ 0.4.0

## 0.4.0 - August 13 2014

* near-complete rewrite from MongoDB to Postgres dependency

## 0.3.0 - March 27 2014

* Initial PyPI release, MongoDB version heavily based on billy
