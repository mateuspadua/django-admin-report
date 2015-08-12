from django.contrib import admin
from products.models import Product


class ProductAdmin( admin.ModelAdmin ):
	# search_fields = ('nome', 'email', 'cpf', 'rg')
	list_display = ('name', 'value')
	# date_hierarchy = 'data'
	# exclude = ('grupo_tributacao',)
admin.site.register( Product, ProductAdmin )
