# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0006_auto_20150702_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributevalue',
            name='feature',
            field=models.ForeignKey(default=5, to='layers.Feature'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attributevalue',
            name='attribute',
            field=models.ForeignKey(to='layers.Attribute'),
        ),
    ]
