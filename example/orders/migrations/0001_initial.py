# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_value'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField(auto_now_add=True, verbose_name=b'Data do Cadastro')),
                ('payment_type', models.PositiveSmallIntegerField(default=None, null=True, blank=True, choices=[(1, 'boleto'), (2, 'cart\xe3o de cr\xe9dito'), (3, 'd\xe9bito')])),
                ('email', models.EmailField(max_length=75, null=True)),
                ('delivered', models.BooleanField(default=False)),
                ('total_value', models.DecimalField(max_digits=11, decimal_places=2)),
                ('gender', models.NullBooleanField(default=None, choices=[(0, 'Male'), (1, 'Female')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='quantity sold')),
                ('value', models.DecimalField(max_digits=11, decimal_places=2)),
                ('order', models.ForeignKey(to='orders.Order')),
                ('product', models.ForeignKey(to='products.Product')),
            ],
            options={
                'verbose_name': 'Order Iten',
                'verbose_name_plural': 'Order Itens',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Order',
                'proxy': True,
                'verbose_name_plural': 'Orders',
            },
            bases=('orders.order',),
        ),
    ]
