# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0005_auto_20150702_0659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='feature',
        ),
        migrations.AddField(
            model_name='attribute',
            name='feature',
            field=models.ManyToManyField(to='layers.Feature'),
        ),
    ]
