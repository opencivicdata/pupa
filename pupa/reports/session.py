from django.db.models import Count, Subquery, OuterRef, Q, F
from opencivicdata.legislative.models import (Bill, VoteEvent, VoteCount, PersonVote,
                                              BillSponsorship)
from ..models import SessionDataQualityReport


def _simple_count(ModelCls, session, **filter):
    return ModelCls.objects.filter(legislative_session_id=session).filter(**filter).count()


def generate_session_report(session):
    report = {
        'bills_missing_actions': _simple_count(Bill, session, actions__isnull=True),
        'bills_missing_sponsors': _simple_count(Bill, session, sponsorships__isnull=True),
        'bills_missing_versions': _simple_count(Bill, session, versions__isnull=True),
        'votes_missing_bill': _simple_count(VoteEvent, session, bill__isnull=True),
        'votes_missing_voters': _simple_count(VoteEvent, session, votes__isnull=True),
        'votes_missing_yes_count': 0,
        'votes_missing_no_count': 0,
        'votes_with_bad_counts': 0,
    }

    voteevents = VoteEvent.objects.filter(legislative_session_id=session)
    queryset = voteevents.annotate(
        yes_sum=Count('pk', filter=Q(votes__option='yes')),
        no_sum=Count('pk', filter=Q(votes__option='no')),
        other_sum=Count('pk', filter=Q(votes__option='other')),
        yes_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                    option='yes').values('value')),
        no_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                   option='no').values('value')),
        other_count=Subquery(VoteCount.objects.filter(vote_event=OuterRef('pk'),
                                                      option='other').values('value')),
    )

    for vote in queryset:
        if vote.yes_count is None:
            report['votes_missing_yes_count'] += 1
            vote.yes_count = 0
        if vote.no_count is None:
            report['votes_missing_no_count'] += 1
            vote.no_count = 0
        if vote.other_count is None:
            vote.other_count = 0
        if (vote.yes_sum != vote.yes_count or
                vote.no_sum != vote.no_count or
                vote.other_sum != vote.other_count):
            report['votes_with_bad_counts'] += 1

    # handle unmatched
    queryset = BillSponsorship.objects.filter(bill__legislative_session_id=session,
                                              entity_type='person', person_id=None
                                              ).values('name').annotate(num=Count('name'))
    report['unmatched_sponsor_people'] = {item['name']: item['num'] for item in queryset}
    queryset = BillSponsorship.objects.filter(bill__legislative_session_id=session,
                                              entity_type='organization', person_id=None
                                              ).values('name').annotate(num=Count('name'))
    report['unmatched_sponsor_organizations'] = {item['name']: item['num'] for item in queryset}
    queryset = PersonVote.objects.filter(vote_event__legislative_session_id=session,
                                         voter__isnull=True).values(name=F('voter_name')).annotate(
                                             num=Count('voter_name')
                                         )
    report['unmatched_voters'] = {item['name']: item['num'] for item in queryset}

    return SessionDataQualityReport(legislative_session_id=session, **report)
