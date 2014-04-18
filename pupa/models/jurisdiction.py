from django.db import models
from .base import CommonBase


class Jurisdiction(CommonBase):
    name = models.CharField(max_length=300)
    url = models.URLField()
    # TODO: division_id link
    # TODO: feature flags as an ArrayField
    # TODO: building_maps?


class JurisdictionSession(CommonBase):
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='sessions')
    name = models.CharField(max_length=300)
    type = models.CharField(max_length=100)     # enum?
    start_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
