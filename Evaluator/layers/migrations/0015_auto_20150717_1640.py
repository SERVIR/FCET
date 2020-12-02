# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
        ('layers', '0014_auto_20150716_2028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feature',
            name='user_map',
        ),
        migrations.AddField(
            model_name='feature',
            name='user_map',
            field=models.ManyToManyField(to='map.Map', through='layers.FeatureStatus'),
        ),
    ]
