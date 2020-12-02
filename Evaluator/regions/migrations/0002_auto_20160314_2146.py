# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='poly',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, blank=True),
        ),
    ]
