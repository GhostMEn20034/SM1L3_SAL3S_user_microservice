from django.contrib import admin

from .models import Cart, CartItem
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at', "cart_uuid", "total", "count")
    list_display = ('user', 'cart_uuid', 'created_at', 'updated_at')


    def total(self, obj):
        return obj.total

    def count(self, obj):
        return obj.count

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', )

    def save_model(self, request, obj, form, change):
        if obj.quantity > 0:
            return super().save_model(request, obj, form, change)

        return self.delete_model(request, obj)
