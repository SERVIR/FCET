# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20150811_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='outcome_year',
            field=models.IntegerField(default=2007),
        ),
    ]
