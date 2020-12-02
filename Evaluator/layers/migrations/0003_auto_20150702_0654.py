# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
        ('layers', '0002_feature_user_map'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='shapefile',
        ),
        migrations.AddField(
            model_name='attribute',
            name='feature',
            field=models.ForeignKey(default=1, to='layers.Feature'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='feature',
            name='user_map',
        ),
        migrations.AddField(
            model_name='feature',
            name='user_map',
            field=models.ManyToManyField(to='map.Map'),
        ),
    ]
