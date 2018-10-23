from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from opencivicdata.core.models import Jurisdiction
from opencivicdata.legislative.models import LegislativeSession


OBJECT_TYPES = (
    ('jurisdiction', 'Jurisdiction'),
    ('person', 'Person'),
    ('organization', 'Organization'),
    ('post', 'Post'),
    ('membership', 'Membership'),
    ('bill', 'Bill'),
    ('vote_event', 'VoteEvent'),
    ('event', 'Event'),
)


class RunPlan(models.Model):
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='runs', on_delete=models.CASCADE)
    success = models.BooleanField(default=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    exception = models.TextField(blank=True, default='')
    traceback = models.TextField(blank=True, default='')


class ScrapeReport(models.Model):
    plan = models.ForeignKey(RunPlan, related_name='scrapers', on_delete=models.CASCADE)
    scraper = models.CharField(max_length=300)
    args = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class ScrapeObjects(models.Model):
    report = models.ForeignKey(ScrapeReport, related_name='scraped_objects',
                               on_delete=models.CASCADE)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    count = models.PositiveIntegerField()


class ImportObjects(models.Model):
    report = models.ForeignKey(RunPlan, related_name='imported_objects', on_delete=models.CASCADE)
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    insert_count = models.PositiveIntegerField()
    update_count = models.PositiveIntegerField()
    noop_count = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Identifier(models.Model):
    identifier = models.CharField(max_length=300)
    jurisdiction = models.ForeignKey(Jurisdiction,
                                     related_name='pupa_ids',
                                     on_delete=models.CASCADE,
                                     )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=300)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):              # __unicode__ on Python 2
        return self.identifier


class SessionDataQualityReport(models.Model):
    legislative_session = models.ForeignKey(LegislativeSession, on_delete=models.CASCADE)

    bills_missing_actions = models.PositiveIntegerField()
    bills_missing_sponsors = models.PositiveIntegerField()
    bills_missing_versions = models.PositiveIntegerField()

    votes_missing_voters = models.PositiveIntegerField()
    votes_missing_bill = models.PositiveIntegerField()
    votes_missing_yes_count = models.PositiveIntegerField()
    votes_missing_no_count = models.PositiveIntegerField()
    votes_with_bad_counts = models.PositiveIntegerField()

    # these fields store lists of names mapped to numbers of occurances
    unmatched_sponsor_people = JSONField()
    unmatched_sponsor_organizations = JSONField()
    unmatched_voters = JSONField()
