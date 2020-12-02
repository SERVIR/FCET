# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0016_auto_20150702_0636'),
        ('layers', '0013_controlledfeature'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('treated', models.BooleanField()),
                ('controlled', models.BooleanField()),
            ],
        ),
        migrations.RemoveField(
            model_name='controlledfeature',
            name='feature_ptr',
        ),
        migrations.RemoveField(
            model_name='treatedfeature',
            name='feature_ptr',
        ),
        migrations.RemoveField(
            model_name='feature',
            name='user_map',
        ),
        migrations.AddField(
            model_name='feature',
            name='user_map',
            field=models.ForeignKey(default=9, to='map.Map'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='ControlledFeature',
        ),
        migrations.DeleteModel(
            name='TreatedFeature',
        ),
        migrations.AddField(
            model_name='featurestatus',
            name='feature',
            field=models.ForeignKey(to='layers.Feature', null=True),
        ),
        migrations.AddField(
            model_name='featurestatus',
            name='user_map',
            field=models.ForeignKey(to='map.Map', null=True),
        ),
    ]
