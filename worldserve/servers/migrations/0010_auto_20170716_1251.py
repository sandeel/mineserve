# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 12:51
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0009_auto_20170716_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 13, 56, 48, 955676, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='server',
            name='id',
            field=models.CharField(default='589089a2-2b70-4029-b196-14af23f6bc1d', max_length=200, primary_key=True, serialize=False),
        ),
    ]