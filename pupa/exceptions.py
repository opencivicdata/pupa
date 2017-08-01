

class PupaError(Exception):
    """ Base class for exceptions from within Pupa """


class PupaInternalError(PupaError):
    """ Indication something went wrong inside of Pupa that never should happen """


class CommandError(PupaError):
    """ Errors from within pupa CLI """


# import-related errors


class DataImportError(PupaError):
    """ A generic error related to the import process. """


class InvalidVoteEventError(DataImportError):
    """ Attempt to create a vote event without an identifier or bill_id """


class NoMembershipsError(DataImportError):
    """ An attempt was made to import a person without any memberships. """

    def __init__(self, ids):
        super(NoMembershipsError, self).__init__('no memberships for {} people: \n{}'.format(
            len(ids), ', '.join(ids))
        )


class SameNameError(DataImportError):
    """ Attempt was made to import two people with the same name. """

    def __init__(self, name):
        super(SameNameError, self).__init__('multiple people with same name "{}" in Jurisdiction '
                                            '- must provide birth_date to disambiguate'
                                            .format(name))


class SameOrgNameError(DataImportError):
    """ Attempt was made to import two orgs with the same name. """

    def __init__(self, name):
        super(SameOrgNameError, self).__init__('multiple orgs with same name "{}" in Jurisdiction '
                                               .format(name))


class DuplicateItemError(DataImportError):
    """ Attempt was made to import items that resolve to the same database item. """

    def __init__(self, data, obj, data_sources=None):
        super(DuplicateItemError, self).__init__(
            'attempt to import data that would conflict with '
            'data already in the import: {} '
            '(already imported as {})\n'
            'obj1 sources: {}\nobj2 sources: {}'.format(
                data,
                obj,
                list(obj.sources.values_list('url', flat=True)
                     if hasattr(obj, 'sources') else []),
                [s['url'] for s in data_sources or []]
            ))


class UnresolvedIdError(DataImportError):
    """ Attempt was made to resolve an id that has no result. """


# scrape-related errors


class ScrapeError(PupaError):
    """ A generic error related to the scrape process. """


class ScrapeValueError(PupaError, ValueError):
    """ An invalid value was passed to a pupa scrape object. """
