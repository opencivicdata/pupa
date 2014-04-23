=================
pupa architecture
=================

pupa.cli
========

* dbinit    - initializes a postgres database for use with pupa scrapers

* init      - initializes a local project directory ready for people to write scrapers

* update    - updates data, can be run with --scrape if desire is to examine data locally

pupa.ext
========

Nothing here is particularly interesting architecturally, this is where a few vendorized files
live.

pupa.scrape
===========

Scraper
-------

All 
