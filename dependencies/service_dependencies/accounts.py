from services.accounts.account_service import AccountService
from .carts import get_cart_service

def get_account_service(account_queryset, user_serializer) -> AccountService:
    cart_service = get_cart_service()
    return AccountService(account_queryset, user_serializer, cart_service)
