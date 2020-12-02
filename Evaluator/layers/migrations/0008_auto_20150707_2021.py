# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0007_auto_20150702_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feature',
            name='shapefile',
            field=models.ForeignKey(to='upload.Upload', null=True),
        ),
    ]
