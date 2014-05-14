import pytest
from pupa.scrape import Vote as ScrapeVote
from pupa.importers import VoteImporter, BillImporter
from opencivicdata.models import VoteEvent, Jurisdiction, JurisdictionSession, Person, Organization


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


@pytest.mark.django_db
def test_full_vote():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    j.sessions.create(name='1900')
    person = Person.objects.create(id='person-id', name='Adam Smith')
    org = Organization.objects.create(id='org-id', name='House', chamber='lower')
    com = Organization.objects.create(id='com-id', name='Arbitrary Committee', parent=org)

    vote = ScrapeVote(session='1900', motion='passage', start_date='1900-04-01',
                      classification='passage', outcome='pass')

    dmi = DumbMockImporter()
    bi = BillImporter('jid', dmi)

    VoteImporter('jid', dmi, dmi, bi).import_data([vote.as_dict()])
