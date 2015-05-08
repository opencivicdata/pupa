from django.db import models
from opencivicdata.models import Jurisdiction


OBJECT_TYPES = (
    ('jurisdiction', 'Jurisdiction'),
    ('person', 'Person'),
    ('organization', 'Organization'),
    ('post', 'Post'),
    ('membership', 'Membership'),
    ('bill', 'Bill'),
    ('vote', 'Vote'),
    ('event', 'Event'),
)


class RunPlan(models.Model):
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='runs')
    success = models.BooleanField(default=True)


class ScrapeReport(models.Model):
    plan = models.ForeignKey(RunPlan, related_name='scrapers')
    scraper = models.CharField(max_length=300)
    args = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class ScrapeObjects(models.Model):
    report = models.ForeignKey(ScrapeReport, related_name='scraped_objects')
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    count = models.PositiveIntegerField()


class ImportObjects(models.Model):
    report = models.ForeignKey(RunPlan, related_name='imported_objects')
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    insert_count = models.PositiveIntegerField()
    update_count = models.PositiveIntegerField()
    noop_count = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Measures(models.Model):
    plan = models.ForeignKey(RunPlan, related_name='measures')
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES)
    measure = models.CharField(max_length=300)
    value = models.FloatField()
