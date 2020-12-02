# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import map.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShapeFileUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shapefile', models.FileField(upload_to=map.models.get_file_path)),
                ('indexfile', models.FileField(upload_to=map.models.get_file_path)),
                ('datafile', models.FileField(upload_to=map.models.get_file_path)),
                ('uid', models.CharField(default=uuid.uuid4, max_length=64)),
            ],
        ),
    ]
