import datetime

from django.db.models import Q
from opencivicdata.models.people_orgs import Post


def post_report(jurisdiction):
    report = {}

    posts = Post.objects.filter(organization__jurisdiction=jurisdiction)

    # Waiting to add `over` until the discussion on `num_seats` is finished
    # https://github.com/opencivicdata/pupa/pull/167
    # report['over']

    today = datetime.date.today().strftime('%Y-%m-%d')
    report['vacant'] = posts.filter(
        Q(end_date__gte=today) | Q(end_date__isnull=True),
        start_date__lte=today).exclude(
        Q(memberships__end_date__gte=today) | Q(memberships__end_date__isnull=True),
        memberships__start_date__lte=today).count()

    return report
