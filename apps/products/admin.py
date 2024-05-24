from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('object_id', 'parent_id', 'event_id', )
    list_display = ('name', 'price', 'stock', 'max_order_qty', )
