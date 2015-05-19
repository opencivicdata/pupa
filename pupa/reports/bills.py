from django.db.models import Count

from opencivicdata.models.bill import Bill
from opencivicdata.models.bill import BillAction
from opencivicdata.models.bill import BillVersion

from .utils import percentage, assert_data_quality_types_exist, get_or_create_type_and_modify


def bill_report(jurisdiction):
    get_or_create_type_and_modify('bill', 'no_versions', (1, None))
    get_or_create_type_and_modify('bill', 'no_actions', (1, None))
    get_or_create_type_and_modify('bill', 'no_sponsors', (1, None))
    get_or_create_type_and_modify('bill', 'no_sponsor_objs', (1, None))
    get_or_create_type_and_modify('bill', 'dup_versions', (1, None))
    get_or_create_type_and_modify('bill', 'unclassified_actions', (1, None))

    report = {}

    bills = Bill.objects.filter(from_organization__jurisdiction=jurisdiction)
    total = bills.count()

    actions = BillAction.objects.filter(bill__from_organization__jurisdiction=jurisdiction)

    versions = BillVersion.objects.filter(bill__from_organization__jurisdiction=jurisdiction)

    report['no_versions'] = percentage(
        bills.filter(versions__isnull=True).count(), total)
    report['no_actions'] = percentage(
        bills.filter(actions__isnull=True).count(), total)
    report['no_sponsors'] = percentage(
        bills.filter(sponsorships__isnull=True).count(), total)
    report['no_sponsor_objs'] = percentage(
        bills.annotate(num_sponsors=Count('sponsorships')).
        filter(num_sponsors=0).count(), total)

    report['dup_versions'] = percentage(
        versions.values('links__url').annotate(url_count=Count('links__url')).
        filter(url_count__gt=1).count(), versions.count())

    report['unclassified_actions'] = percentage(
        actions.filter(classification__isnull=True).count(), actions.count())

    assert_data_quality_types_exist('bill', report)
    return report
