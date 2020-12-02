# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_id', models.BigIntegerField(null=True)),
                ('date', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'date')),
                ('upload_dir', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_file', models.FileField(upload_to=b'uploads')),
                ('slug', models.SlugField(blank=True)),
                ('upload', models.ForeignKey(blank=True, to='upload.Upload', null=True)),
            ],
        ),
    ]
