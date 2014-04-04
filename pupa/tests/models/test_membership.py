from nose.tools import raises
from pupa.models import Membership


@raises(ValueError)
def test_basic_invalid_membership():
    """ Make sure that we can create an invalid membership and break """
    membership = Membership("person_id", "orga_id")
    membership.validate()

    membership.person_id = 33
    membership.validate()


def test_contact_details_on_membership():
    """ Ensure contact details work for memberships """
    membership = Membership("person_id", "orga_id")
    membership.validate()

    membership.add_contact_detail(type='address', value='bar', note='baz')
    membership.validate()
