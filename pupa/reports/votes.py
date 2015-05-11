from opencivicdata.models.vote import VoteEvent, VoteCount, PersonVote


def vote_report(jurisdiction):
    report = {}

    votes = VoteEvent.objects.filter(organization__jurisdiction=jurisdiction)

    report['invalid'] = 0
    for vote in votes:
        person_votes = PersonVote.objects.filter(vote=vote)
        vote_counts = VoteCount.objects.filter(vote=vote)

        is_invalid = False
        for vote_option in vote_counts.values_list('option', flat=True):
            roll_call_count = person_votes.filter(option=vote_option).count()
            official_count = vote_counts.get(option=vote_option).value
            if roll_call_count != official_count:
                is_invalid = True

        if is_invalid:
            report['invalid'] += 1

    return report
