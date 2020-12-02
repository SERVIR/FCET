# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(max_length=128)),
                ('sub_region', models.CharField(max_length=128, null=True)),
                ('region', models.CharField(max_length=128)),
                ('poly', django.contrib.gis.db.models.fields.PolygonField(srid=4326, blank=True)),
                ('bbox', models.CharField(max_length=255, null=True)),
            ],
        ),
    ]
