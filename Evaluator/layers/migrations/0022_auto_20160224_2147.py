# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
        ('layers', '0021_auto_20160104_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='FastFeatureStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('set_type', models.CharField(default=b'ERROR', max_length=12, choices=[(b'SELECTED', b'SELECTED'), (b'TREATED', b'TREATED'), (b'CONTROLLED', b'CONTROLLED'), (b'MATCHED', b'MATCHED'), (b'FORESTFILTER', b'FORESTFILTER'), (b'ERROR', b'ERROR')])),
                ('feature_set', django.contrib.postgres.fields.ArrayField(default=list, base_field=models.IntegerField(), size=None)),
                ('user_map', models.ForeignKey(to='map.Map', null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='fastfeaturestatus',
            unique_together=set([('user_map', 'set_type')]),
        ),
    ]
