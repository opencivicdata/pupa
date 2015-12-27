import pytest
from pupa.scrape import Event as ScrapeEvent
from pupa.importers import EventImporter, OrganizationImporter, PersonImporter, BillImporter, VoteEventImporter
from opencivicdata.models import Jurisdiction, Event, Person, Membership, Organization, Bill, VoteEvent

def ge():
    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00Z",
        location_name="America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    return event

oi = OrganizationImporter('jid')
pi = PersonImporter('jid')
bi = BillImporter('jid', oi, pi)
vei = VoteEventImporter('jid', pi, oi, bi)

@pytest.mark.django_db
def test_related_people_event():
    Jurisdiction.objects.create(id='jid', division_id='did')
    george = Person.objects.create(id='gw', name='George Washington')
    john = Person.objects.create(id='jqp', name='John Q. Public')
    o = Organization.objects.create(name='Merica', jurisdiction_id='jid')

    Membership.objects.create(person=george, organization=o)
    Membership.objects.create(person=john, organization=o)

    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_person(person="John Q. Public")

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1

    assert Event.objects.get(name="America's Birthday").participants.first().person_id == 'gw'

    assert Event.objects.get(name="America's Birthday").agenda.first().related_entities.first().person_id == 'jqp'


@pytest.mark.django_db
def test_related_vote_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900', identifier='1900')
    org = Organization.objects.create(id='org-id', name='House', classification='lower')
    bill = Bill.objects.create(id='bill-1', identifier='HB 1', 
                               legislative_session=session)
    vote = VoteEvent.objects.create(id='vote-1', 
                                    identifier="Roll no. 12",
                                    bill=bill, 
                                    legislative_session=session,
                                    organization=org)
                               
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_vote_event(vote_event="Roll no. 12")

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1

    assert Event.objects.get(name="America's Birthday").agenda.first().related_entities.first().vote_event_id == 'vote-1'


@pytest.mark.django_db
def test_related_bill_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900', identifier='1900')
    org = Organization.objects.create(id='org-id', name='House', classification='lower')
    bill = Bill.objects.create(id='bill-1', identifier='HB 101', 
                               legislative_session=session)
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_bill(bill="HB 101")

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1

    assert Event.objects.get(name="America's Birthday").agenda.first().related_entities.first().bill_id == 'bill-1'


@pytest.mark.django_db
def test_related_committee_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    session = j.legislative_sessions.create(name='1900', identifier='1900')
    org = Organization.objects.create(id='org-id', name='House', 
                                      classification='lower', 
                                      jurisdiction=j)
    com = Organization.objects.create(id='fiscal', name="Fiscal Committee", 
                                      classification='committee',
                                      parent=org,
                                      jurisdiction=j)

    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_committee(committee="Fiscal Committee")

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1

    assert Event.objects.get(name="America's Birthday").agenda.first().related_entities.first().organization_id == 'fiscal'


@pytest.mark.django_db
def test_media_event():
    Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_media_link(
            note="Hello, World",
            media_type='application/octet-stream',
            url="http://hello.world/foo"
        )

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_media_document():
    Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        event.add_document(note="Presentation",
                           url="http://example.com/presentation.pdf")

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_full_event():
    Jurisdiction.objects.create(id='jid', division_id='did')
    george = Person.objects.create(id='gw', name='George Washington')
    o = Organization.objects.create(name='Merica', jurisdiction_id='jid')
    Membership.objects.create(person=george, organization=o)

    event = ge()

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event.as_dict()])
    assert result['event']['insert'] == 1

    event = ge()
    
    result = EventImporter('jid', oi, pi, bi, vei).import_data([event.as_dict()])
    assert result['event']['noop'] == 1

    event = ge()
    event.location['name'] = "United States of America"
    result = EventImporter('jid', oi, pi, bi, vei).import_data([event.as_dict()])
    assert result['event']['update'] == 1


@pytest.mark.django_db
def test_bad_event_time():
    Jurisdiction.objects.create(id='jid', division_id='did')
    event = ge()
    event.start_time = "2014-07-04T05:00"
    pytest.raises(
        ValueError,
        EventImporter('jid', oi, pi, bi, vei).import_item,
        event.as_dict()
    )


@pytest.mark.django_db
def test_top_level_media_event():
    Jurisdiction.objects.create(id='jid', division_id='did')
    event1, event2 = ge(), ge()

    event1.add_media_link("fireworks", "http://example.com/fireworks.mov",
                          media_type='application/octet-stream')
    event2.add_media_link("fireworks", "http://example.com/fireworks.mov",
                          media_type='application/octet-stream')

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid', oi, pi, bi, vei).import_data([event2.as_dict()])
    assert result['event']['noop'] == 1
