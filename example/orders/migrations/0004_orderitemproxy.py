# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_value'),
        ('orders', '0003_auto_20141225_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItemProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Order Item',
                'proxy': True,
                'verbose_name_plural': 'Order Items',
            },
            bases=('products.product',),
        ),
    ]
