# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='total',
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2, blank=True),
            preserve_default=True,
        ),
    ]
