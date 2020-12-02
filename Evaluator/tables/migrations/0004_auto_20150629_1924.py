# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0003_auto_20150526_2011'),
    ]

    operations = [
        migrations.CreateModel(
            name='CBStests',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.CharField(default=b'', max_length=100, blank=True)),
                ('pseudo_r2', models.FloatField()),
                ('LR_chi2', models.FloatField()),
                ('chi2_pvalue', models.FloatField()),
                ('mean_bias', models.FloatField()),
                ('med_bias', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='CheckSensitivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gamma', models.DecimalField(max_digits=2, decimal_places=1)),
                ('q_plus', models.FloatField()),
                ('q_minus', models.FloatField()),
                ('p_plus', models.FloatField()),
                ('p_minus', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('variable', models.CharField(default=b'', max_length=100, blank=True)),
                ('sample', models.CharField(default=b'', max_length=100, blank=True)),
                ('treated', models.FloatField()),
                ('controls', models.FloatField()),
                ('difference', models.FloatField()),
                ('standard_error', models.FloatField()),
                ('t_stat', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='WorldBorder',
        ),
    ]
