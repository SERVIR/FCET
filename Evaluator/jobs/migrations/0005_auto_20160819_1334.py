# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0017_shapefileupload'),
        ('jobs', '0004_job_outcome_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('session_start', models.DateTimeField()),
                ('country', models.CharField(default=b'', max_length=50)),
                ('region_type', models.CharField(default=b'', max_length=50)),
                ('state', models.CharField(default=b'', max_length=50)),
                ('min_forest_cover', models.CharField(default=b'', max_length=50)),
                ('max_forest_cover', models.CharField(default=b'', max_length=50)),
                ('agroforest', models.CharField(default=b'', max_length=50)),
                ('agriculture', models.CharField(default=b'', max_length=50)),
                ('forest', models.CharField(default=b'', max_length=50)),
                ('treatment_area_option', models.CharField(default=b'', max_length=50)),
                ('control_area_option', models.CharField(default=b'', max_length=50)),
            ],
        ),
        migrations.RenameField(
            model_name='job',
            old_name='outcome_year',
            new_name='high_outcome_year',
        ),
        migrations.AddField(
            model_name='job',
            name='low_outcome_year',
            field=models.IntegerField(default=2007),
        ),
        migrations.AddField(
            model_name='job',
            name='usermap',
            field=models.ForeignKey(default=9, to='map.Map'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jobstats',
            name='job_id',
            field=models.ForeignKey(to='jobs.Job'),
        ),
    ]
