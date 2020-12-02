# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0002_auto_20150629_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date'),
        ),
    ]
