# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0005_auto_20150702_0715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbsmeans',
            name='job',
            field=models.ForeignKey(to='jobs.Job'),
        ),
        migrations.AlterField(
            model_name='cbstests',
            name='job',
            field=models.ForeignKey(to='jobs.Job'),
        ),
        migrations.AlterField(
            model_name='checksensitivity',
            name='job',
            field=models.ForeignKey(to='jobs.Job'),
        ),
        migrations.AlterField(
            model_name='results',
            name='job',
            field=models.ForeignKey(to='jobs.Job'),
        ),
    ]
