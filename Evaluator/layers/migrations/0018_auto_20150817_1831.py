# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0017_auto_20150811_1846'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='featurestatus',
            unique_together=set([('user_map', 'feature')]),
        ),
    ]
