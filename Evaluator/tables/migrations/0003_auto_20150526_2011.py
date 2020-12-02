# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0002_auto_20150526_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worldborder',
            name='aspect',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='dem',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='dis_to_cit',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='distoclear',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='forest_cov',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='forest_los',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='grid_code',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='im_2010',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='marginaliz',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='oppcost',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='pdensity',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='protected',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='slope',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='state',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='state_num',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='temp',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='tenure_typ',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='worldborder',
            name='ttime_min',
            field=models.FloatField(null=True),
        ),
    ]
