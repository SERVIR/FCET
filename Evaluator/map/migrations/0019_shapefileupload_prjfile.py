# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import map.models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0018_auto_20160819_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='shapefileupload',
            name='prjfile',
            field=models.FileField(null=True, upload_to=map.models.get_file_path),
        ),
    ]
