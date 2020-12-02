# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0004_remove_attributevalue_feature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributevalue',
            name='attribute',
            field=models.OneToOneField(to='layers.Attribute'),
        ),
    ]
