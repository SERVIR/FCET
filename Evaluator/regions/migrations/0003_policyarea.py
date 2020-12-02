# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0002_auto_20160314_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('poly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, blank=True)),
                ('shapefile_name', models.CharField(max_length=128)),
            ],
        ),
    ]
