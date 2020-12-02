# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20150811_1852'),
        ('tables', '0006_auto_20150702_0718'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultsChart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100, blank=True)),
                ('data', models.FloatField()),
                ('job', models.ForeignKey(to='jobs.Job')),
            ],
        ),
        migrations.CreateModel(
            name='ResultsChartManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
    ]
