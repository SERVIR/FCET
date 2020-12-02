# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0015_auto_20150717_1640'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feature',
            old_name='user_map',
            new_name='user_maps',
        ),
    ]
