# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
        ('layers', '0008_auto_20150707_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='user_map',
            field=models.ForeignKey(default=9, to='map.Map'),
            preserve_default=False,
        ),
    ]
