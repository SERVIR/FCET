# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_auto_20160819_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='current',
            field=models.NullBooleanField(default=False),
        ),
    ]
