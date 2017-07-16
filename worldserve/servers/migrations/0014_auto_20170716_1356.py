# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 13:56
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0013_auto_20170716_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='expiry_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 15, 1, 47, 831160, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='server',
            name='id',
            field=models.CharField(default='0bf53b3d-7282-413f-85d0-df0115d9feab', max_length=200, primary_key=True, serialize=False),
        ),
    ]