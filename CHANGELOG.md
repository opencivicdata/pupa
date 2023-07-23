# pupa changelog

## 0.11.0 - April 3 2023

Improvements:

* Add `pupa clean` command to delete database objects that haven't been seen in recent scrapes

## 0.10.2 - March 18 2021

Improvements:

* allow null event locations
* resolve memberships based on start date, falling back to end date if no start date is available

Fixes:

* raise exception for whitespace in urls

## 0.10.1 - March 23 2020

Improvements:

* fire post-save hook on imports
* check family_name when resolving names

Fixes:

* if scrapers are omitted on command line, use all scrapers again

## 0.10.0 - December 11 2019

Improvements:

* add data quality reports that update after each import (requires migration)
* add flags to disable person, bill, vote, event import
* let date be set on event media & document

Fixes:

* Fix warnings from obsolete usage of importlib & jsonschema
* remove parties from tests
* don't call check_session_list if running import only
* add support for Post.maximum_memberships
* add support for Person given & family names
* stop testing on Postgres 9.x

## 0.9.1 - October 23 2018

Fixes:

* minor packaging fixes & dependency pinning tweaks


## 0.9.0 - February 14 2018

Backwards-incompatible changes:

* fix_bill_id is no longer called on bill identifiers

Improvements:

* django 2.0 compatibility fixes (on_delete on models)
* require python-opencivicdata 2.1 fixes
* drop validictory for jsonschema
* add 'pupa party' command for atomic addition of parties, deprecate Jurisdiction.parties
* add IMPORT_TRANSFORMERS setting allowing alterations of data on import

Fixes:

* bugfix for OrganizationImporter other_names
* bugfix for VoteEvent bill resolution
* bugfix for VoteEvent bill action resolution (#307)


## 0.8.0 - July 19 2017

Backwards-incompatible changes:

* role no longer defaults to 'member' and is now optional in Person constructor
  when used w/ primary_org. if primary_org alone is unambiguous scrapers
  can set primary org alone and role will be set automatically
* in accordance w/ OCDEP101, Event.start_time/end_time are now
  Event.start_date/end_date

Improvements:

* allow extras to be set on bill actions & event agenda items
* bill actions can now specify times
* add classification field to event agenda items
* resolving organizations checks other names like we do for people

## 0.7.0 - June 5 2017

Backwards-incompatible changes:

* moves from split dependency of opencivicdata-divisions/opencivicdata-django
  to new unified opencivicdata which also splits into two Django apps
  (see python-opencivicdata release notes for more detail)

Improvements:

* allow Memberships to have unresolved `person_name` similar to how other
  name resolutions work
* allow linking of VoteEvent to BillAction by setting a matching chamber,
  date, and bill\_action
* add Scraper.latest\_session convienience method
* optionally allow setting \_scraped\_name on legislative\_session, which will
  be used in session\_list checking if present
* add concept of Pupa identifiers, to aid in resolution

Fixes:

* pupa dbinit --reset now correctly drops dependent pupa tables and migrations
* exit gracefully if the first scrape fails instead of complaining about RunPlan
  DB constraint
* complex psuedo-ids are now deterministic (by sorting dict keys)


## 0.6.0 - February 19 2017

Backwards-incompatible changes:

* Identify sessions by their identifiers instead of their names (update your `get_session_list()` methods)

Improvements:

* Check for the presence of a `get_session_list()` method instead of `check_sessions = True`
* Resolve an event's participants and its agenda items' related entities #206, #207
* Accept an organization name in `Person.add_membership` for the second parameter #233
* Accept `datetime` dates wherever string dates are accepted #218
* Improve error reporting #214, #230, #231
* Compatible with Django 1.10

Fixes:

* Allow people to hold multiple posts in an organization #244, #247
* Add a `primary_org_name` parameter to `Person.add_term`, to disambiguate organizations with the same classification #223
* Update an object if the explicit order of its related objects has changed #242
* Touch an object's `updated_at` whenever its related objects are updated #226
* Correctly resolve a new person with the same name #232
* Don't raise a resolution error due to multiple matches in cases where zero matches are acceptable

## 0.5.2 - November 18 2015

* show run logs in the admin
* start tracking failed runs

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
