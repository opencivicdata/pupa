from django.db.models import Count

from opencivicdata.models.bill import Bill
from opencivicdata.models.bill import BillAction
from opencivicdata.models.bill import BillVersion

from .utils import percentage


def bill_report(jurisdiction):
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

    return report
