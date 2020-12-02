# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('layers', '0022_auto_20160224_2147'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_id', models.BigIntegerField(null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date')),
                ('upload_dir', models.CharField(max_length=100, null=True)),
                ('name', models.CharField(max_length=64, null=True)),
                ('geom_type', models.CharField(max_length=50)),
                ('encoding', models.CharField(max_length=20)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_file', models.FileField(upload_to=b'uploads')),
                ('slug', models.SlugField(blank=True)),
                ('upload', models.ForeignKey(blank=True, to='layers.Upload', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='feature',
            name='bulk_ref',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feature',
            name='row_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attribute',
            name='shapefile',
            field=models.ForeignKey(to='layers.Upload', null=True),
        ),
        migrations.AlterField(
            model_name='feature',
            name='shapefile',
            field=models.ForeignKey(to='layers.Upload', null=True),
        ),
    ]
