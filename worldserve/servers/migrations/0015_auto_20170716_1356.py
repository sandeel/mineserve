# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 13:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0014_auto_20170716_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 15, 1, 55, 683852, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='server',
            name='id',
            field=models.CharField(default='d5d7560a-bc2c-4769-a295-95c168140822', max_length=200, primary_key=True, serialize=False),
        ),
    ]
