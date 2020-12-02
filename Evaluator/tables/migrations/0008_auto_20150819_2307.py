# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0007_resultschart_resultschartmanager'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ResultsChartManager',
        ),
        migrations.RenameField(
            model_name='resultschart',
            old_name='data',
            new_name='data_values',
        ),
    ]
