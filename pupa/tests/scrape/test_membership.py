import pytest
from pupa.scrape import Membership


def test_basic_invalid_membership():
    """ Make sure that we can create an invalid membership and break """
    membership = Membership("person_id", "orga_id")
    membership.validate()

    membership.person_id = 33
    with pytest.raises(ValueError):
        membership.validate()
