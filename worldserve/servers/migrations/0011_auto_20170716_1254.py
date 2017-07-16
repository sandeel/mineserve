# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 12:54
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0010_auto_20170716_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 13, 59, 58, 969554, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='server',
            name='id',
            field=models.CharField(default='a07bbba3-d663-486c-9b07-5f3aa8a4a4cc', max_length=200, primary_key=True, serialize=False),
        ),
    ]