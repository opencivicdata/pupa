# Generated by Django 2.1.2 on 2018-10-23 15:25

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("legislative", "0005_auto_20171005_2028"),
        ("pupa", "0006_identifier_jurisdiction"),
    ]

    operations = [
        migrations.CreateModel(
            name="SessionDataQualityReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bills_missing_actions", models.PositiveIntegerField()),
                ("bills_missing_sponsors", models.PositiveIntegerField()),
                ("bills_missing_versions", models.PositiveIntegerField()),
                ("votes_missing_voters", models.PositiveIntegerField()),
                ("votes_missing_bill", models.PositiveIntegerField()),
                ("votes_missing_yes_count", models.PositiveIntegerField()),
                ("votes_missing_no_count", models.PositiveIntegerField()),
                ("votes_with_bad_counts", models.PositiveIntegerField()),
                (
                    "unmatched_sponsor_people",
                    django.contrib.postgres.fields.jsonb.JSONField(),
                ),
                (
                    "unmatched_sponsor_organizations",
                    django.contrib.postgres.fields.jsonb.JSONField(),
                ),
                ("unmatched_voters", django.contrib.postgres.fields.jsonb.JSONField()),
                (
                    "legislative_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="legislative.LegislativeSession",
                    ),
                ),
            ],
        ),
    ]
