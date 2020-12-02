# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('map', '0015_auto_20150702_0630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='user',
        ),
        migrations.AddField(
            model_name='map',
            name='user',
            field=models.OneToOneField(default=16, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
