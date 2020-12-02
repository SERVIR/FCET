# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('matching_method', models.CharField(max_length=50, choices=[(b'PSM', b'Propensity Score Matching'), (b'MM', b'Mahalanobis Matching')])),
                ('matching_estimator', models.CharField(max_length=50, choices=[(b'NN', b'Nearest Neighbor')])),
                ('covariate_variables', models.TextField()),
                ('outcome_variables', models.TextField()),
                ('caliper_distance', models.IntegerField()),
                ('common_support', models.BooleanField()),
                ('standard_error_type', models.CharField(max_length=50, choices=[(b'SIMPLE', b'simple'), (b'CLUSTER', b'cluster'), (b'BOOTSTRAP', b'bootstrap'), (b'AI', b'Abadie and Imbens')])),
                ('geo_query', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
    ]
