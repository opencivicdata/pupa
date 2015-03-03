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
            field=models.CharField(choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote', 'Vote'), ('event', 'Event'), ('disclosure', 'Disclosure')], max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='importobjects',
            name='report',
            field=models.ForeignKey(related_name='imported_objects', to='pupa.RunPlan'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='runplan',
            name='jurisdiction',
            field=models.ForeignKey(related_name='runs', to='opencivicdata.Jurisdiction'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapeobjects',
            name='object_type',
            field=models.CharField(choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote', 'Vote'), ('event', 'Event'), ('disclosure', 'Disclosure')], max_length=20),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapeobjects',
            name='report',
            field=models.ForeignKey(related_name='scraped_objects', to='pupa.ScrapeReport'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='scrapereport',
            name='plan',
            field=models.ForeignKey(related_name='scrapers', to='pupa.RunPlan'),
            preserve_default=True,
        ),
    ]
