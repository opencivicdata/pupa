import pytest
from pupa.scrape import VoteEvent, Bill, Organization, OrderVoteEvent
from pupa.utils import get_pseudo_id


def toy_vote_event():
    ve = VoteEvent(legislative_session="2009", motion_text="passage of the bill",
                   start_date="2009-01-07", result='pass', classification='bill-passage')
    ve.add_source("http://uri.example.com/", note="foo")
    return ve


def test_simple_vote_event():
    ve = toy_vote_event()
    ve.set_count('yes', 2)
    ve.yes('James')
    ve.no('Paul')
    ve.vote('abstain', 'Thom')

    assert len(ve.votes) == 3
    assert len(ve.counts) == 1
    assert get_pseudo_id(ve.organization) == {'classification': 'legislature'}
    assert get_pseudo_id(ve.votes[0]['voter_id']) == {'name': 'James'}
    assert get_pseudo_id(ve.votes[1]['voter_id']) == {'name': 'Paul'}
    assert get_pseudo_id(ve.votes[2]['voter_id']) == {'name': 'Thom'}
    assert ve.bill is None

    ve.validate()
    assert 'we get here'


def test_vote_event_org_obj():
    o = Organization('something', classification='committee')
    ve = VoteEvent(legislative_session="2009", motion_text="passage of the bill",
                   start_date="2009-01-07", result='pass', classification='bill-passage',
                   organization=o)
    assert ve.organization == o._id


def test_vote_event_org_dict():
    odict = {'name': 'Random Committee', 'classification': 'committee'}
    ve = VoteEvent(legislative_session="2009", motion_text="passage of the bill",
                   start_date="2009-01-07", result='pass', classification='bill-passage',
                   organization=odict)
    assert get_pseudo_id(ve.organization) == odict


def test_vote_event_org_chamber():
    ve = VoteEvent(legislative_session="2009", motion_text="passage of the bill",
                   start_date="2009-01-07", result='pass', classification='bill-passage',
                   chamber='upper')
    assert get_pseudo_id(ve.organization) == {'classification': 'upper'}


def test_org_and_chamber_conflict():
    with pytest.raises(ValueError):
        VoteEvent(legislative_session="2009", motion_text="passage of the bill",
                  start_date="2009-01-07", result='pass', classification='passage',
                  organization='test', chamber='lower')


def test_set_count():
    ve = toy_vote_event()
    ve.set_count('yes', 2)
    ve.set_count('no', 100)
    ve.set_count('yes', 0)
    assert ve.counts == [{'option': 'yes', 'value': 0}, {'option': 'no', 'value': 100}]


def test_set_bill_obj():
    ve = toy_vote_event()
    b = Bill('HB 1', legislative_session='2009', title='fake bill')
    ve.set_bill(b)
    assert ve.bill == b._id


def test_set_bill_obj_no_extra_args():
    ve = toy_vote_event()
    b = Bill('HB 1', legislative_session='2009', title='fake bill')
    with pytest.raises(ValueError):
        ve.set_bill(b, chamber='lower')


def test_set_bill_pseudo_id():
    ve = toy_vote_event()
    ve.set_bill('HB 1', chamber='lower')
    assert get_pseudo_id(ve.bill) == {'identifier': 'HB 1',
                                      'from_organization__classification': 'lower',
                                      'legislative_session__identifier': '2009',
                                      }


def test_str():
    ve = toy_vote_event()
    s = str(ve)
    assert ve.legislative_session in s
    assert ve.motion_text in s


def test_order_vote_event():
    ve = toy_vote_event()
    order_vote_event = OrderVoteEvent()

    # add order as seconds to date with no time
    ve.start_date = '2019-01-01'
    ve.end_date = None
    order_vote_event('2019', '1', ve)
    assert ve.start_date == '2019-01-01T00:00:01'
    assert ve.end_date is None

    # add order as seconds to time with explicit midnight time and zone, preserving timezone
    ve.start_date = '2019-01-01T00:00:00+05:00'
    ve.end_date = ''
    order_vote_event('2019', '1', ve)
    assert ve.start_date == '2019-01-01T00:00:02+05:00'
    assert ve.end_date == ''

    # a second bill should start with '00:00:01' again
    ve.start_date = '2019-01-01'
    ve.end_date = None
    order_vote_event('2019', '2', ve)
    assert ve.start_date == '2019-01-01T00:00:01'
    assert ve.end_date is None

    # the same bill id in a different session should start with '00:00:01' again
    ve.start_date = '2019-01-01'
    ve.end_date = None
    order_vote_event('2020', '1', ve)
    assert ve.start_date == '2019-01-01T00:00:01'
    assert ve.end_date is None

    # add order as seconds to time with explicit midnight time and no timezone
    ve.start_date = ve.end_date = '2019-01-01T00:00:00'
    order_vote_event('2019', '1', ve)
    assert ve.start_date == '2019-01-01T00:00:03'
    assert ve.end_date == '2019-01-01T00:00:03'

    # don't change a date with a non-midnight time
    ve.start_date = '2019-01-01T00:00:55+05:00'
    order_vote_event('2019', '1', ve)
    assert ve.start_date == '2019-01-01T00:00:55+05:00'
