# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('legislative', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportObjects',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('object_type', models.CharField(max_length=20, choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote_event', 'VoteEvent'), ('event', 'Event')])),
                ('insert_count', models.PositiveIntegerField()),
                ('update_count', models.PositiveIntegerField()),
                ('noop_count', models.PositiveIntegerField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RunPlan',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('success', models.BooleanField(default=True)),
                ('jurisdiction', models.ForeignKey(to='core.Jurisdiction', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='importobjects',
            name='report',
            field=models.ForeignKey(to='pupa.RunPlan', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ScrapeObjects',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('object_type', models.CharField(max_length=20, choices=[('jurisdiction', 'Jurisdiction'), ('person', 'Person'), ('organization', 'Organization'), ('post', 'Post'), ('membership', 'Membership'), ('bill', 'Bill'), ('vote_event', 'VoteEvent'), ('event', 'Event')])),
                ('count', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScrapeReport',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('scraper', models.CharField(max_length=300)),
                ('args', models.CharField(max_length=300)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('plan', models.ForeignKey(to='pupa.RunPlan', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scrapeobjects',
            name='report',
            field=models.ForeignKey(to='pupa.ScrapeReport', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
