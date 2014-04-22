from django.db import models
from djorm_pgarray.fields import ArrayField

from .base import CommonBase, LinkBase


class Jurisdiction(CommonBase):
    id = models.CharField(max_length=500, primary_key=True)
    name = models.CharField(max_length=300)
    url = models.URLField()
    feature_flags = ArrayField(dbtype="text")
    # TODO: division_id link


class JurisdictionSession(CommonBase):
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='sessions')
    name = models.CharField(max_length=300)
    type = models.CharField(max_length=100)     # enum?
    start_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]


class JurisdictionBuildingMap(LinkBase):
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='building_maps')
    order = models.PositiveIntegerField()
