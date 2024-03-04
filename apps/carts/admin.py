from .models import Cart, CartItem
from services.carts.cart_synchronizer import CartSynchronizer

from django.contrib import admin
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at', "cart_uuid")
    list_display = ('user', 'cart_uuid', 'total', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart' ,'product', 'quantity', )

    def save_model(self, request, obj, form, change):
        if obj.quantity > 0:
            cart_synchronizer = CartSynchronizer(obj)
            if change:
                cart_synchronizer.sync_cart_item_update()
            else:
                cart_synchronizer.sync_cart_item_create()

            return super().save_model(request, obj, form, change)

        return self.delete_model(request, obj)

    def delete_model(self, request, obj):
        cart_synchronizer = CartSynchronizer(obj)
        cart_synchronizer.sync_cart_item_delete()
        return super().delete_model(request, obj)
