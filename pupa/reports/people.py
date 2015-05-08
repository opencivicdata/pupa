from opencivicdata.models.people_orgs import Person

from .utils import percentage


def person_report(jurisdiction):
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

    return report
