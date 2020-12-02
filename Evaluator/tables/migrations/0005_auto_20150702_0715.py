# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        ('tables', '0004_auto_20150629_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='cbsmeans',
            name='job',
            field=models.OneToOneField(default=1, to='jobs.Job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cbstests',
            name='job',
            field=models.OneToOneField(default=1, to='jobs.Job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='checksensitivity',
            name='job',
            field=models.OneToOneField(default=1, to='jobs.Job'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='results',
            name='job',
            field=models.OneToOneField(default=1, to='jobs.Job'),
            preserve_default=False,
        ),
    ]
