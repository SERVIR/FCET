# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='encoding',
            field=models.CharField(default='LATIN-1', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='upload',
            name='geom_type',
            field=models.CharField(default='Point', max_length=50),
            preserve_default=False,
        ),
    ]
