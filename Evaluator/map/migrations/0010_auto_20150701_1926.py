# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0009_map_map_feature'),
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
            name='state',
            field=models.TextField(default='st'),
            preserve_default=False,
        ),
    ]
