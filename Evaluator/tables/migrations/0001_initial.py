# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CBSmeans',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100, blank=True)),
                ('sample', models.CharField(default=b'', max_length=100, blank=True)),
                ('treated', models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True)),
                ('control', models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True)),
                ('bias', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('biasr', models.DecimalField(null=True, max_digits=4, decimal_places=1, blank=True)),
                ('t', models.DecimalField(null=True, max_digits=4, decimal_places=2, blank=True)),
                ('pt', models.DecimalField(null=True, max_digits=4, decimal_places=3, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorldBorder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pointid', models.IntegerField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('state', models.CharField(max_length=100)),
                ('state_num', models.IntegerField()),
                ('forest_cov', models.IntegerField()),
                ('forest_los', models.IntegerField()),
                ('slope', models.FloatField()),
                ('aspect', models.FloatField()),
                ('dem', models.FloatField()),
                ('ttime_min', models.FloatField()),
                ('pdensity', models.FloatField()),
                ('dis_to_cit', models.FloatField()),
                ('rain', models.IntegerField()),
                ('temp', models.FloatField()),
                ('protected', models.IntegerField()),
                ('grid_code', models.IntegerField()),
                ('oppcost', models.FloatField()),
                ('tenure_typ', models.IntegerField()),
                ('im_2010', models.FloatField()),
                ('marginaliz', models.IntegerField()),
                ('distoclear', models.FloatField()),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
    ]
