# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pupa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataQualityChecks',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('value', models.FloatField()),
                ('plan', models.ForeignKey(related_name='checks', to='pupa.RunPlan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataQualityTypes',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('object_type', models.CharField(choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote', 'Vote'), ('event', 'Event')], max_length=20)),
                ('name', models.CharField(max_length=300)),
                ('is_percentage', models.BooleanField()),
                ('bad_range', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dataqualitychecks',
            name='type',
            field=models.ForeignKey(related_name='checks', to='pupa.DataQualityTypes'),
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
