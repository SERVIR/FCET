# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_job_current'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobstats',
            name='country',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
