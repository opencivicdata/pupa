import pytest
from pupa.scrape import (VoteEvent as ScrapeVoteEvent, Bill as ScrapeBill, Organization as
                         ScrapeOrganization, Person as ScrapePerson)
from pupa.importers import (VoteEventImporter, BillImporter, MembershipImporter,
                            OrganizationImporter, PersonImporter)
from opencivicdata.models import (VoteEvent, Jurisdiction, LegislativeSession, Person,
                                  Organization, Bill)


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


@pytest.mark.django_db
def test_full_vote_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.legislative_sessions.create(name='1900', identifier='1900')
    sp1 = ScrapePerson('John Smith', primary_org='lower')
    sp2 = ScrapePerson('Adam Smith', primary_org='lower')
    org = ScrapeOrganization(name='House', classification='lower')
    bill = ScrapeBill('HB 1', '1900', 'Axe & Tack Tax Act', from_organization=org._id)
    vote_event = ScrapeVoteEvent(legislative_session='1900', motion_text='passage',
                                 start_date='1900-04-01', classification='passage:bill',
                                 result='pass', bill_chamber='lower', bill='HB 1',
                                 organization=org._id)
    vote_event.set_count('yes', 20)
    vote_event.yes('John Smith')
    vote_event.no('Adam Smith')

    oi = OrganizationImporter('jid')
    oi.import_data([org.as_dict()])

    pi = PersonImporter('jid')
    pi.import_data([sp1.as_dict(), sp2.as_dict()])

    mi = MembershipImporter('jid', pi, oi, DumbMockImporter())
    mi.import_data([sp1._related[0].as_dict(), sp2._related[0].as_dict()])

    bi = BillImporter('jid', oi, pi)
    bi.import_data([bill.as_dict()])

    VoteEventImporter('jid', pi, oi, bi).import_data([vote_event.as_dict()])

    assert VoteEvent.objects.count() == 1
    ve = VoteEvent.objects.get()
    assert ve.legislative_session == LegislativeSession.objects.get()
    assert ve.motion_classification == ['passage:bill']
    assert ve.bill == Bill.objects.get()
    count = ve.counts.get()
    assert count.option == 'yes'
    assert count.value == 20
    votes = list(ve.votes.all())
    assert len(votes) == 2
    for v in ve.votes.all():
        if v.voter_name == 'John Smith':
            assert v.option == 'yes'
            assert v.voter == Person.objects.get(name='John Smith')
        else:
            assert v.option == 'no'
            assert v.voter == Person.objects.get(name='Adam Smith')


@pytest.mark.django_db
def test_vote_event_identifier_dedupe():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.legislative_sessions.create(name='1900', identifier='1900')

    vote_event = ScrapeVoteEvent(legislative_session='1900', start_date='2013',
                                 classification='anything', result='passed',
                                 motion_text='a vote on something',
                                 identifier='Roll Call No. 1')
    dmi = DumbMockImporter()
    bi = BillImporter('jid', dmi, dmi)

    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'insert'
    assert VoteEvent.objects.count() == 1

    # same exact vote event, no changes
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'noop'
    assert VoteEvent.objects.count() == 1

    # new info, update
    vote_event.result = 'failed'
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'update'
    assert VoteEvent.objects.count() == 1

    # new bill, insert
    vote_event.identifier = 'Roll Call 2'
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'insert'
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_bill_id_dedupe():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900', identifier='1900')
    org = Organization.objects.create(id='org-id', name='House', classification='lower')
    bill = Bill.objects.create(id='bill-1', identifier='HB 1', legislative_session=session,
                               from_organization=org)
    bill2 = Bill.objects.create(id='bill-2', identifier='HB 2', legislative_session=session,
                                from_organization=org)

    vote_event = ScrapeVoteEvent(legislative_session='1900', start_date='2013',
                                 classification='anything', result='passed',
                                 motion_text='a vote on something',
                                 bill=bill.identifier, bill_chamber='lower')
    dmi = DumbMockImporter()
    bi = BillImporter('jid', dmi, dmi)

    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'insert'
    assert VoteEvent.objects.count() == 1

    # same exact vote event, no changes
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'noop'
    assert VoteEvent.objects.count() == 1

    # new info, update
    vote_event.result = 'failed'
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'update'
    assert VoteEvent.objects.count() == 1

    # new vote event, insert
    vote_event = ScrapeVoteEvent(legislative_session='1900', start_date='2013',
                                 classification='anything', result='passed',
                                 motion_text='a vote on something',
                                 bill=bill2.identifier, bill_chamber='lower')
    _, what = VoteEventImporter('jid', dmi, dmi, bi).import_item(vote_event.as_dict())
    assert what == 'insert'
    assert VoteEvent.objects.count() == 2


@pytest.mark.django_db
def test_vote_event_bill_clearing():
    # ensure that we don't wind up with vote events sitting around forever on bills as
    # changes make it look like there are multiple vote events
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900', identifier='1900')
    org = Organization.objects.create(id='org-id', name='House', classification='lower')
    bill = Bill.objects.create(id='bill-1', identifier='HB 1', legislative_session=session,
                               from_organization=org)
    Bill.objects.create(id='bill-2', identifier='HB 2', legislative_session=session,
                        from_organization=org)
    dmi = DumbMockImporter()
    bi = BillImporter('jid', dmi, dmi)

    vote_event1 = ScrapeVoteEvent(legislative_session='1900', start_date='2013',
                                  classification='anything', result='passed',
                                  motion_text='a vote on somthing',             # typo intentional
                                  bill=bill.identifier, bill_chamber='lower')
    vote_event2 = ScrapeVoteEvent(legislative_session='1900', start_date='2013',
                                  classification='anything', result='passed',
                                  motion_text='a vote on something else',
                                  bill=bill.identifier, bill_chamber='lower')

    # have to use import_data so postimport is called
    VoteEventImporter('jid', dmi, dmi, bi).import_data([
        vote_event1.as_dict(),
        vote_event2.as_dict()
    ])
    assert VoteEvent.objects.count() == 2

    # a typo is fixed, we don't want 3 vote events now
    vote_event1.motion_text = 'a vote on something'
    VoteEventImporter('jid', dmi, dmi, bi).import_data([
        vote_event1.as_dict(),
        vote_event2.as_dict()
    ])
    assert VoteEvent.objects.count() == 2
