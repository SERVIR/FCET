# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0016_auto_20150717_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featurestatus',
            name='controlled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='featurestatus',
            name='treated',
            field=models.BooleanField(default=False),
        ),
    ]
