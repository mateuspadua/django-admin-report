from django.db import models


class Product(models.Model):
	name = models.CharField("Product name", max_length=255)
	value = models.DecimalField(max_digits=11, decimal_places=2)

	def __unicode__(self):
		return self.name
