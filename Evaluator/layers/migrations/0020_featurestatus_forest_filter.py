# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0019_featurestatus_matched'),
    ]

    operations = [
        migrations.AddField(
            model_name='featurestatus',
            name='forest_filter',
            field=models.BooleanField(default=False),
        ),
    ]
