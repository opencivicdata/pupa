import pytest
from pupa.scrape import Vote, Bill, Organization
from pupa.utils import get_psuedo_id


def toy_vote():
    v = Vote(legislative_session="2009", motion_text="passage of the bill",
             start_date="2009-01-07", result='pass', classification='passage:bill')
    v.add_source("http://uri.example.com/", note="foo")
    return v


def test_simple_vote():
    v = toy_vote()
    v.set_count('yes', 2)
    v.yes('James')
    v.no('Paul')
    v.vote('abstain', 'Thom')

    assert len(v.votes) == 3
    assert len(v.counts) == 1
    assert get_psuedo_id(v.organization) == {'classification': 'legislature'}
    assert v.bill is None

    v.validate()
    assert 'we get here'


def test_vote_org_obj():
    o = Organization('something')
    v = Vote(legislative_session="2009", motion_text="passage of the bill",
             start_date="2009-01-07", result='pass', classification='passage:bill', organization=o)
    assert v.organization == o._id


def test_vote_org_dict():
    odict = {'name': 'Random Committee', 'classification': 'committee'}
    v = Vote(legislative_session="2009", motion_text="passage of the bill",
             start_date="2009-01-07", result='pass', classification='passage:bill',
             organization=odict)
    assert get_psuedo_id(v.organization) == odict


def test_vote_org_chamber():
    v = Vote(legislative_session="2009", motion_text="passage of the bill",
             start_date="2009-01-07", result='pass', classification='passage:bill',
             chamber='upper')
    assert get_psuedo_id(v.organization) == {'classification': 'legislature', 'chamber': 'upper'}


def test_org_and_chamber_conflict():
    with pytest.raises(ValueError):
        Vote(legislative_session="2009", motion_text="passage of the bill",
             start_date="2009-01-07", result='pass', classification='passage', organization='test',
             chamber='lower')


def test_set_count():
    v = toy_vote()
    v.set_count('yes', 2)
    v.set_count('no', 100)
    v.set_count('yes', 0)
    assert v.counts == [{'option': 'yes', 'value': 0}, {'option': 'no', 'value': 100}]


def test_set_bill_obj():
    v = toy_vote()
    b = Bill('HB 1', legislative_session='2009', title='fake bill')
    v.set_bill(b)
    assert v.bill == b._id


def test_set_bill_obj_no_extra_args():
    v = toy_vote()
    b = Bill('HB 1', legislative_session='2009', title='fake bill')
    with pytest.raises(ValueError):
        v.set_bill(b, chamber='lower')


def test_set_bill_psuedo_id():
    v = toy_vote()
    v.set_bill('HB 1', chamber='lower')
    assert get_psuedo_id(v.bill) == {'identifier': 'HB 1',
                                     'from_organization__classification': 'legislature',
                                     'from_organization__chamber': 'lower'}


def test_str():
    v = toy_vote()
    s = str(v)
    assert v.legislative_session in s
    assert v.motion_text in s
