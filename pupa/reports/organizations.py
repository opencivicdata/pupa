import datetime

from django.db.models import Q
from opencivicdata.models.people_orgs import Organization

from .utils import assert_data_quality_types_exist, get_or_create_type_and_modify


def organization_report(jurisdiction):
    get_or_create_type_and_modify('organization', 'empty_committees', (1, None), False)

    report = {}

    organizations = Organization.objects.filter(jurisdiction=jurisdiction)

    report['empty_committees'] = 0
    today = datetime.date.today().strftime('%Y-%m-%d')
    for committee in organizations.filter(
            Q(dissolution_date__gte=today) | Q(dissolution_date=''),
            Q(founding_date__lte=today) | Q(founding_date=''),
            classification='committee'):
        if committee.memberships.all().filter(
                Q(end_date__gte=today) | Q(end_date=''),
                start_date__lte=today).count() == 0:
            report['empty_committees'] += 1

    assert_data_quality_types_exist('organization', report)
    return report
