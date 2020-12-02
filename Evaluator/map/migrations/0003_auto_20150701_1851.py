# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0002_auto_20150701_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='forest_cover',
            field=models.FloatField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='map',
            name='map_feature',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='map',
            name='state',
            field=models.TextField(default='st'),
            preserve_default=False,
        ),
    ]
