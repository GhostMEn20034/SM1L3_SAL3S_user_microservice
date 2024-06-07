from apps.carts.models import Cart

class CartAccountService:
    """
    Responsible for interaction between user and cart entities
    """
    @staticmethod
    def create_cart_on_signup(user_instance) -> Cart:
        created_cart = Cart.objects.create(user=user_instance)
        return created_cart
