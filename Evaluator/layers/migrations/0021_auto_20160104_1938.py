# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0020_featurestatus_forest_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featurestatus',
            name='forest_filter',
            field=models.BooleanField(default=True),
        ),
    ]
