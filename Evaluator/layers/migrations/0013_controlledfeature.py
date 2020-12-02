# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0012_treatedfeature'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlledFeature',
            fields=[
                ('feature_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='layers.Feature')),
                ('controlled', models.BooleanField()),
            ],
            bases=('layers.feature',),
        ),
    ]
