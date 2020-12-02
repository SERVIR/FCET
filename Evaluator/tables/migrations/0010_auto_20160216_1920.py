# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0009_auto_20150908_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checksensitivity',
            name='gamma',
            field=models.DecimalField(max_digits=3, decimal_places=1),
        ),
        migrations.AlterField(
            model_name='checksensitivity',
            name='p_minus',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='checksensitivity',
            name='p_plus',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='checksensitivity',
            name='q_minus',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='checksensitivity',
            name='q_plus',
            field=models.FloatField(null=True),
        ),
    ]
