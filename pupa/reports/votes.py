from django.db.models import Count
from django.db.models import Q
from opencivicdata.models.vote import VoteEvent

from .utils import percentage


def vote_report(jurisdiction):
    report = {}

    votes = VoteEvent.objects.filter(organization__jurisdiction=jurisdiction)
    total = votes.count()

    report['invalid'] = percentage(
        votes.annotate(yeses=Count('counts__yes')).filter(Q(votes='counts__yes') | Q())

    return report
