from django.db import models


class CommonBase(models.Model):
    """ common base fields across all top-level models """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeFIeld(auto_now=True)

    class Meta:
        abstract = True


class ContactDetailBase(models.Model):
    type = models.CharField(max_length=50)
    value = models.CharField(max_length=300, blank=True)
    note = models.CharField(max_length=300, blank=True)
    label = models.CharField(max_length=300, blank=True)

    class Meta:
        abstract = True


class IdentifierBase(models.Model):
    identifier = models.CharField(max_length=300)
    scheme = models.CharField(max_length=300)

    class Meta:
        abstract = True


class OtherNameBase(models.Model):
    name = models.CharField(max_length=500)
    note = models.CharField(max_length=500, blank=True)
    start_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10)      # YYYY[-MM[-DD]]

    class Meta:
        abstract = True


class LinkBase(models.Model):
    note = models.CharField(max_length=300, blank=True)
    url = models.URLField()

    class Meta:
        abstract = True
