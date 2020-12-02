# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0003_auto_20150702_0654'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attributevalue',
            name='feature',
        ),
    ]
