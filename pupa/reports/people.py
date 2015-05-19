from opencivicdata.models.people_orgs import Person

from .utils import percentage, assert_data_quality_types_exist, get_or_create_type_and_modify


def person_report(jurisdiction):
    get_or_create_type_and_modify('person', 'no_address', (1, None))
    get_or_create_type_and_modify('person', 'no_email', (1, None))
    get_or_create_type_and_modify('person', 'no_phone', (1, None))
    get_or_create_type_and_modify('person', 'no_image', (1, None))

    report = {}

    people = Person.objects.filter(memberships__organization__jurisdiction=jurisdiction)
    total = people.count()

    # Contact details
    report['no_address'] = percentage(
        people.exclude(contact_details__type='address').count(), total)
    report['no_email'] = percentage(
        people.exclude(contact_details__type='email').count(), total)
    report['no_phone'] = percentage(
        people.exclude(contact_details__type='voice').count(), total)

    report['no_image'] = percentage(
        people.filter(image__isnull=True).count(), total)

    assert_data_quality_types_exist('person', report)
    return report
