# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pupa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importobjects',
            name='object_type',
            field=models.CharField(max_length=20, choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote', 'Vote'), ('event', 'Event'), ('disclosure', 'Disclosure')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='importobjects',
            name='report',
            field=models.ForeignKey(to='pupa.RunPlan', related_name='imported_objects'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='runplan',
            name='jurisdiction',
            field=models.ForeignKey(to='opencivicdata.Jurisdiction', related_name='runs'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapeobjects',
            name='object_type',
            field=models.CharField(max_length=20, choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote', 'Vote'), ('event', 'Event'), ('disclosure', 'Disclosure')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapeobjects',
            name='report',
            field=models.ForeignKey(to='pupa.ScrapeReport', related_name='scraped_objects'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapereport',
            name='plan',
            field=models.ForeignKey(to='pupa.RunPlan', related_name='scrapers'),
            preserve_default=True,
        ),
    ]
