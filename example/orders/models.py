# -*- coding: utf-8 -*-

from django.db import models
from products.models import Product

# Create your models here.

PAYMENT_TYPE = (
		(1, u"boleto"),
		(2, u"cartão de crédito"),
		(3, u"débito"),
	)

GENDER = (
	(0, u"Male"),
	(1, u"Female")
)


class Order(models.Model):
	data = models.DateField(auto_now_add=True, verbose_name='Data do Cadastro')
	payment_type = models.PositiveSmallIntegerField(default=None, choices=PAYMENT_TYPE, blank=True, null=True)
	email = models.EmailField(null=True)
	delivered = models.BooleanField(default=False)
	total_value = models.DecimalField(max_digits=11, decimal_places=2)
	gender = models.NullBooleanField(choices=GENDER, null=True, blank=True, default=None)

	def __unicode__(self):
		return str(self.id)


class OrderItem(models.Model):
	class Meta:
		verbose_name, verbose_name_plural = u"Order Iten", u"Order Itens"

	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	quantity = models.PositiveSmallIntegerField(verbose_name=u'quantity sold')
	value = models.DecimalField(max_digits=11, decimal_places=2)
	total = models.DecimalField(max_digits=11, decimal_places=2, blank=True, default=0)

	def save(self, *args, **kwargs):
		self.total = self.quantity * self.value
		super(OrderItem, self).save(*args, **kwargs)


class OrderProxy(Order):
	class Meta:
		verbose_name, verbose_name_plural = u"Report Order", u"Report Orders"
		proxy = True


class ProductProxy(Product):
	class Meta:
		verbose_name, verbose_name_plural = u"Report Order Item", u"Report Order Items"
		proxy = True
