# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
        ('layers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='user_map',
            field=models.ForeignKey(default=1, to='map.Map'),
            preserve_default=False,
        ),
    ]
