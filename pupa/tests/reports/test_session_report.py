import pytest
import django
from opencivicdata.core.models import Jurisdiction, Division, Organization, Person
from opencivicdata.legislative.models import Bill, VoteEvent
from pupa.reports import generate_session_report


def create_data():
    Division.objects.create(id='ocd-division/country:us', name='USA')
    j = Jurisdiction.objects.create(id='jid', division_id='ocd-division/country:us')
    org = Organization.objects.create(jurisdiction=j, name='House', classification='lower')
    person = Person.objects.create(name='Roy')
    j.legislative_sessions.create(identifier='1899', name='1899')
    session = j.legislative_sessions.create(identifier='1900', name='1900').id
    return session, org, person


@pytest.mark.django_db
def test_bills_missing_actions():
    session, org, person = create_data()
    Bill.objects.create(identifier='HB1', title='One', legislative_session_id=session)
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)

    report = generate_session_report(session)
    assert report.bills_missing_actions == 2

    b.actions.create(description='Introduced', order=1, organization=org)
    report = generate_session_report(session)
    assert report.bills_missing_actions == 1


@pytest.mark.django_db
def test_bills_missing_sponsors():
    session, org, person = create_data()
    Bill.objects.create(identifier='HB1', title='One', legislative_session_id=session)
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)

    report = generate_session_report(session)
    assert report.bills_missing_sponsors == 2

    b.sponsorships.create(name='Roy', entity_type='person')
    report = generate_session_report(session)
    assert report.bills_missing_sponsors == 1


@pytest.mark.django_db
def test_bills_missing_versions():
    session, org, person = create_data()
    Bill.objects.create(identifier='HB1', title='One', legislative_session_id=session)
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)

    report = generate_session_report(session)
    assert report.bills_missing_versions == 2

    b.versions.create(note='Final Copy')
    report = generate_session_report(session)
    assert report.bills_missing_versions == 1


@pytest.mark.django_db
def test_votes_missing_bill():
    session, org, person = create_data()
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)
    v = VoteEvent.objects.create(legislative_session_id=session, motion_text='Passage',
                                 organization=org)
    VoteEvent.objects.create(legislative_session_id=session, motion_text='Amendment',
                             organization=org)

    report = generate_session_report(session)
    assert report.votes_missing_bill == 2

    v.bill = b
    v.save()
    report = generate_session_report(session)
    assert report.votes_missing_bill == 1


@pytest.mark.django_db
def test_votes_missing_voters():
    session, org, person = create_data()
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)
    v = VoteEvent.objects.create(legislative_session_id=session, motion_text='Passage', bill=b,
                                 organization=org)
    VoteEvent.objects.create(legislative_session_id=session, motion_text='Amendment', bill=b,
                             organization=org)

    report = generate_session_report(session)
    assert report.votes_missing_voters == 2

    v.votes.create(option='yes', voter_name='Speaker')
    report = generate_session_report(session)
    assert report.votes_missing_voters == 1


@pytest.mark.django_db
def test_missing_yes_no_counts():
    session, org, person = create_data()
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)
    v = VoteEvent.objects.create(legislative_session_id=session, motion_text='Passage', bill=b,
                                 organization=org)
    VoteEvent.objects.create(legislative_session_id=session, motion_text='Amendment', bill=b,
                             organization=org)

    report = generate_session_report(session)
    assert report.votes_missing_yes_count == 2
    assert report.votes_missing_no_count == 2

    v.counts.create(option='yes', value=1)
    report = generate_session_report(session)
    assert report.votes_missing_yes_count == 1
    assert report.votes_missing_no_count == 2

    v.counts.create(option='no', value=0)
    report = generate_session_report(session)
    assert report.votes_missing_yes_count == 1
    assert report.votes_missing_no_count == 1


@pytest.mark.skipif(django.VERSION[0] < 2, reason="bug in Django 1.11")
@pytest.mark.django_db
def test_votes_with_bad_counts():
    session, org, person = create_data()
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)
    v = VoteEvent.objects.create(legislative_session_id=session, motion_text='Passage', bill=b,
                                 organization=org)

    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 0

    # add count, breaking
    v.counts.create(option='yes', value=1)
    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 1

    # add voter, fixing
    v.votes.create(option='yes', voter_name='One')
    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 0

    # add voter, breaking
    v.votes.create(option='no', voter_name='Two')
    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 1

    # add count, still not equal
    v.counts.create(option='no', value=2)
    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 1

    # add voter, fixing
    v.votes.create(option='no', voter_name='Three')
    report = generate_session_report(session)
    assert report.votes_with_bad_counts == 0


@pytest.mark.django_db
def test_unmatched_sponsors():
    session, org, person = create_data()
    b1 = Bill.objects.create(identifier='HB1', title='One', legislative_session_id=session)
    b2 = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)

    b1.sponsorships.create(name='Roy', entity_type='person')
    b1.sponsorships.create(name='Wendy', entity_type='person')
    b1.sponsorships.create(name='Committee On Legislation', entity_type='organization')

    b2.sponsorships.create(name='Wendy', entity_type='person')

    report = generate_session_report(session)
    assert len(report.unmatched_sponsor_people) == 2
    assert report.unmatched_sponsor_people['Roy'] == 1
    assert report.unmatched_sponsor_people['Wendy'] == 2
    assert report.unmatched_sponsor_organizations == {'Committee On Legislation': 1}

    # ensure that Roy goes away when linked
    sp = b1.sponsorships.get(name='Roy')
    sp.person_id = person.id
    sp.save()
    report = generate_session_report(session)
    assert report.unmatched_sponsor_people == {'Wendy': 2}


@pytest.mark.django_db
def test_unmatched_voters():
    session, org, person = create_data()
    b = Bill.objects.create(identifier='HB2', title='Two', legislative_session_id=session)
    v1 = VoteEvent.objects.create(legislative_session_id=session, motion_text='Passage', bill=b,
                                  organization=org)
    v2 = VoteEvent.objects.create(legislative_session_id=session, motion_text='Override', bill=b,
                                  organization=org)

    report = generate_session_report(session)
    assert report.unmatched_voters == {}

    # add voters
    v1.votes.create(option='yes', voter_name='Roy')
    v1.votes.create(option='yes', voter_name='Wendy')
    v2.votes.create(option='yes', voter_name='Wendy')
    report = generate_session_report(session)
    assert len(report.unmatched_voters) == 2
    assert report.unmatched_voters['Roy'] == 1
    assert report.unmatched_voters['Wendy'] == 2

    # ensure that Roy goes away when linked
    voter = v1.votes.get(voter_name='Roy')
    voter.voter_id = person.id
    voter.save()
    report = generate_session_report(session)
    assert report.unmatched_voters == {'Wendy': 2}
