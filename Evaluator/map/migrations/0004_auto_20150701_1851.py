# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0003_auto_20150701_1851'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='forest_cover',
        ),
        migrations.RemoveField(
            model_name='map',
            name='map_feature',
        ),
        migrations.RemoveField(
            model_name='map',
            name='state',
        ),
    ]
