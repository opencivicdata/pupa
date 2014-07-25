

class PupaError(Exception):
    """ Base class for exceptions from within Pupa """


class PupaInternalError(PupaError):
    """ Indication something went wrong inside of Pupa that never should happen """


class DataImportError(PupaError):
    """ A generic error related to the import process. """


class InvalidVoteError(DataImportError):
    """ Attempt to create a vote without an identifier or bill_id """


class NoMembershipsError(DataImportError):
    """ An attempt was made to import a person without any memberships. """

    def __init__(self, ids):
        super(NoMembershipsError, self).__init__('no memberhips for {} people: \n{}'.format(
            len(ids), ', '.join(ids))
        )

class SameNameError(DataImportError):
    """ Attempt was made to import two people with the same name. """

    def __init__(self, name):
        super(SameNameError, self).__init__('multiple people with same name "{}" in Jurisdiction '
                                            '- must provide birth_date to disambiguate'
                                            .format(name))


class UnresolvedIdError(DataImportError):
    """ Attempt was made to resolve an id that has no result. """
