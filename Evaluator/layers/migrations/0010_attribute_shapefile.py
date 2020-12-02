# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0002_auto_20150629_2034'),
        ('layers', '0009_attribute_user_map'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='shapefile',
            field=models.ForeignKey(to='upload.Upload', null=True),
        ),
    ]
