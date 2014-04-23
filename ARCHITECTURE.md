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

scrape.Scraper - base class for all scrapers

    self.info
    self.debug
    self.warning
    self.error
    self.critical

    self.save_object(obj) - given a scrape object saves it to disk
        calls obj.prepare(jid), obj.as_dict(), and obj.validate()

    self.do_scrape(**kwargs) - the workhorse of the scraper, runs a scrape by calling self.scrape()
        passed on all arbitrary args to scrape, which can use them for discrimination

    self.scrape(**kwargs) - the user-implemented method where the scraper should be implemented


scrape.BaseBillScraper - special helper for bill scrapers

    ContinueScraping - exception that can be raised to skip a bill

    scrape() defined to call two functions
        get_bill_ids(**kwargs) - returns a list of (bill_id, extras) tuples
        get_bill(bill_id, **extras) - either gets a bill or raises a ContinueScraping


scrape.BaseModel - base class for all scrape models
    _type - overriden to the type (???used where???)
    _schema - the schema dictionary to use in validate()

    self._id - defaults to a UUID
    self._related - list of related models
    self._meta - ???used???
    self.extras = {} - dict of all irregular fields

    validate() - validates against _schema
    as_dict() - converts to a dict, only includes properties in the schema

    notes:
        setattr is overriden to avoid setting properties that will fail on save
        __eq__ is overriden (???used???)


scrape.SourceMixin, ContactDetailMixin, LinkMixin, AssociatedLinkMixin
    various mixins that add common fields and helper methods for each of these common attributes
