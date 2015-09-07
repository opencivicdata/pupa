import pytest
from pupa.scrape import Disclosure as ScrapeDisclosure
from pupa.importers import (DisclosureImporter, OrganizationImporter,
                            PersonImporter, EventImporter)
from opencivicdata.models import Jurisdiction


def gd():
    disclosure = ScrapeDisclosure(
        classification="lobbying",
        effective_date="2011-01-22T00:00Z",
        submitted_date="2011-03-17T00:00Z",
        timezone="America/New_York"
    )
    return disclosure


@pytest.mark.django_db
def test_disclosure():
    j = Jurisdiction.objects.create(id='jid', division_id='did')

    disclosure = gd()

    disclosure.add_source(
        url="http://www.example.com/",
        note="This is the source"
    )

    oi = OrganizationImporter('jid')
    pi = PersonImporter('jid')
    ei = EventImporter('jid', org_importer=oi, person_importer=pi)

    result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data(
                                    [disclosure.as_dict()])
    assert result['disclosure']['insert'] == 1

    result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data([disclosure.as_dict()])
    assert result['disclosure']['noop'] == 1


@pytest.mark.django_db
def test_disclosure_no_source():
    j = Jurisdiction.objects.create(id='jid', division_id='did')

    disclosure = gd()
    
    oi = OrganizationImporter('jid')
    pi = PersonImporter('jid')
    ei = EventImporter('jid', org_importer=oi, person_importer=pi)

    with pytest.raises(KeyError):
        result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data([disclosure.as_dict()])


@pytest.mark.django_db
def test_disclosure_source_identified():
    j = Jurisdiction.objects.create(id='jid', division_id='did')

    disclosure1 = gd()
    disclosure2 = gd()

    disclosure1.add_source(
        url="http://www.example.com/",
        note="This is the source"
    )
    disclosure2.add_source(
        url="http://www.ejemplo.com/",
        note="This is a different source"
    )
    
    oi = OrganizationImporter('jid')
    pi = PersonImporter('jid')
    ei = EventImporter('jid', org_importer=oi, person_importer=pi)

    result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data([disclosure1.as_dict()])
    assert result['disclosure']['insert'] == 1

    result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data([disclosure1.as_dict()])
    assert result['disclosure']['noop'] == 1

    result = DisclosureImporter('jid', org_importer=oi, person_importer=pi,
                                event_importer=ei).import_data([disclosure2.as_dict()])
    assert result['disclosure']['insert'] == 1
