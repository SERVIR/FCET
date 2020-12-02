# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0011_auto_20150714_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreatedFeature',
            fields=[
                ('feature_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='layers.Feature')),
                ('treated', models.BooleanField()),
            ],
            bases=('layers.feature',),
        ),
    ]
