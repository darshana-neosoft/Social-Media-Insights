# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-26 07:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('webfetchapp', '0005_youtube_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtube_data',
            name='vedio_id',
            field=models.CharField(default=datetime.datetime(2016, 10, 26, 7, 50, 40, 23494, tzinfo=utc), max_length=300),
            preserve_default=False,
        ),
    ]
