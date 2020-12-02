# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0018_auto_20150817_1831'),
    ]

    operations = [
        migrations.AddField(
            model_name='featurestatus',
            name='matched',
            field=models.BooleanField(default=False),
        ),
    ]
