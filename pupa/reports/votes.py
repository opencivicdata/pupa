from opencivicdata.models.vote import VoteEvent, VoteCount, PersonVote
from .utils import assert_data_quality_types_exist, get_or_create_type_and_modify


def vote_report(jurisdiction):
    get_or_create_type_and_modify('vote', 'invalid', (1, None), False)

    report = {}

    votes = VoteEvent.objects.filter(organization__jurisdiction=jurisdiction)

    report['invalid'] = 0
    for vote in votes:
        person_votes = PersonVote.objects.filter(vote=vote)
        vote_counts = VoteCount.objects.filter(vote=vote)

        for vote_option in vote_counts.values_list('option', flat=True):
            roll_call_count = person_votes.filter(option=vote_option).count()
            official_count = vote_counts.get(option=vote_option).value
            if roll_call_count != official_count:
                report['invalid'] += 1
                break

    assert_data_quality_types_exist('vote', report)
    return report
