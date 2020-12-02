# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0010_attribute_shapefile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='user_map',
            field=models.ForeignKey(to='map.Map', null=True),
        ),
    ]
