from django.urls import path

from .views import CartViewSet


def get_url_patterns():
    get_cart_details = CartViewSet.as_view(
        {'get': 'retrieve'}
    )
    create_cart_item = CartViewSet.as_view(
        {'post': 'create_cart_item'}
    )
    update_or_delete_cart_item = CartViewSet.as_view(
        {
            'patch': 'update_cart_item',
            'delete': 'delete_cart_item',
        }
    )
    clear_cart = CartViewSet.as_view(
        {'post': 'clear_cart'}
    )

    urlpatterns = [
        path('<cart_uuid>/', get_cart_details, name='cart-detail'),
        path('<cart_uuid>/items/', create_cart_item, name='create-cart-item'),
        path('<cart_uuid>/items/<item_id>/', update_or_delete_cart_item, name='update-or-delete-cart-item'),
        path('<cart_uuid>/clear/', clear_cart, name='clear-cart'),
    ]

    return urlpatterns
