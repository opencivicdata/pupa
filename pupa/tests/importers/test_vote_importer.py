import pytest
from pupa.scrape import Vote as ScrapeVote
from pupa.importers import VoteImporter, BillImporter
from opencivicdata.models import VoteEvent, Jurisdiction, Person, Organization, Bill


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


@pytest.mark.django_db
def test_full_vote():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900')
    person = Person.objects.create(id='person-id', name='Adam Smith')
    org = Organization.objects.create(id='org-id', name='House', chamber='lower',
                                      classification='legislature')
    bill = Bill.objects.create(id='bill-id', identifier='HB 1', session=session,
                               from_organization=org)
    com = Organization.objects.create(id='com-id', name='Arbitrary Committee', parent=org)

    vote = ScrapeVote(session='1900', motion='passage', start_date='1900-04-01',
                      classification='passage:bill', outcome='pass', bill=bill.identifier)
    vote.set_count('yes', 20)
    vote.yes('John Smith')
    vote.no('Adam Smith')

    dmi = DumbMockImporter()
    bi = BillImporter('jid', dmi)

    VoteImporter('jid', dmi, dmi, bi).import_data([vote.as_dict()])

    assert VoteEvent.objects.count() == 1
    ve = VoteEvent.objects.get()
    assert ve.session_id == session.id
    assert ve.classification == ['passage:bill']
    assert ve.bill_id == bill.id
    count = ve.counts.get()
    assert count.option == 'yes'
    assert count.value == 20
    votes = list(ve.votes.all())
    assert len(votes) == 2
    for v in ve.votes.all():
        if v.voter_name == 'John Smith':
            assert v.option == 'yes'
        else:
            assert v.option == 'no'
