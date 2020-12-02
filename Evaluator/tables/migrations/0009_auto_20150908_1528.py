# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0008_auto_20150819_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbsmeans',
            name='bias',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='cbsmeans',
            name='biasr',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='cbsmeans',
            name='pt',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='cbsmeans',
            name='t',
            field=models.DecimalField(null=True, max_digits=11, decimal_places=5, blank=True),
        ),
    ]
