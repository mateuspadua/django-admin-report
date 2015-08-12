# django-admin-report
Create reports using the full potential of django admin

Django-Admin-Report
==============

This is a [Django](https://www.djangoproject.com/) app project

The app includes admin_report Mixin.

Installation
============

1. Install `django_admin_report`

        pip install django_admin_report

2. Add `admin_report` to your `INSTALLED_APPS` in your project settings in firstly. Example:

		INSTALLED_APPS = (
		    'admin_report',  # firstly
		    'import_export',
		    'django.contrib.admin',
		    ...
		)

Documentation
============

How use:

1. First: look this model.py. This example is inside this project in the "example" folder
		
		class Product(models.Model):
			name = models.CharField("Product name", max_length=255)
			value = models.DecimalField(max_digits=11, decimal_places=2)

			def __unicode__(self):
				return self.name


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


2. Second: in your app, add in your model.py one proxy model to model that you desired create report, like this:
		
		class ProductProxy(Product):
			class Meta:
				verbose_name, verbose_name_plural = u"Report Order Item", u"Report Order Items"
				proxy = True 	

3. Third: in your admin.py create one Admin using ChartReportAdmin
		
		from django.db.models import Sum, Avg, Count, Min, Max
		from admin_report.mixins import ChartReportAdmin

		.....

		class ReportOrderItemsAdmin(ChartReportAdmin):
			list_display = ('name', 'orderitem__value__avg', 'orderitem__value__max', 'orderitem__value__min', 'orderitem__quantity__sum', 'orderitem__total__sum',)

			report_annotates = (
				("orderitem__quantity", Sum, "subtotal total items sold"),
				("orderitem__total", Sum, "subtotal total value sold"),
				("orderitem__value", Avg, "product sold average"),
				("orderitem__value", Max, "higher sold value"),
				("orderitem__value", Min, "lower sold value"),
			)

			report_aggregates = (
				('orderitem__total__sum', Sum, "<b>Total: R$ %value</b>"),
				('orderitem__quantity', Sum, "total items sold"),
			)

		admin.site.register( ProductProxy, ReportOrderItemsAdmin )

4. Fourth: More details about properties, soon.