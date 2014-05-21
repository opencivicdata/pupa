import pytest
from pupa.scrape import Event as ScrapeEvent
from pupa.importers import EventImporter
from opencivicdata.models import Event, Jurisdiction


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


@pytest.mark.django_db
def test_full_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    #session = j.sessions.create(name='1900')
    #person = Person.objects.create(id='person-id', name='Adam Smith')
    #org = Organization.objects.create(id='org-id', name='House', chamber='lower',
    #                                  classification='legislature')
    #bill = Bill.objects.create(id='bill-id', name='HB 1', session=session, from_organization=org)
    #com = Organization.objects.create(id='com-id', name='Arbitrary Committee', parent=org)

    #vote = ScrapeVote(session='1900', motion='passage', start_date='1900-04-01',
    #                  classification='passage:bill', outcome='pass', bill=bill.name)
    #vote.set_count('yes', 20)
    #vote.yes('John Smith')
    #vote.no('Adam Smith')
    event = ScrapeEvent(name="America's Birthday", start_time="2014-07-04", location="America",
                        all_day=True)
    event.add_person("George Washington")
    event.add_media_link("fireworks", "http://example.com/fireworks.mov")

    #dmi = DumbMockImporter()
    #bi = BillImporter('jid', dmi)

    EventImporter('jid').import_data([event.as_dict()])

    #assert VoteEvent.objects.count() == 1
    #ve = VoteEvent.objects.get()
    #assert ve.session_id == session.id
    #assert ve.classification == ['passage:bill']
    #assert ve.bill_id == bill.id
    #count = ve.counts.get()
    #assert count.option == 'yes'
    #assert count.value == 20
    #votes = list(ve.votes.all())
    #assert len(votes) == 2
    #for v in ve.votes.all():
    #    if v.voter_name == 'John Smith':
    #        assert v.option == 'yes'
    #    else:
    #        assert v.option == 'no'
