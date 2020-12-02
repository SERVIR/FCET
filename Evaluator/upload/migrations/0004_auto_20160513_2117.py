# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0023_auto_20160513_2117'),
        ('upload', '0003_auto_20150908_1528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='upload',
            name='user',
        ),
        migrations.RemoveField(
            model_name='uploadfile',
            name='upload',
        ),
        migrations.DeleteModel(
            name='Upload',
        ),
        migrations.DeleteModel(
            name='UploadFile',
        ),
    ]
