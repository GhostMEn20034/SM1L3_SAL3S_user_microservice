from typing import Dict, Any, List

from django.contrib.auth import get_user_model

from apps.accounts.serializers.replication_serializers import UserReplicationSerializer
from apps.carts.models import Cart, CartItem
from apps.core.tasks import perform_data_replication
from ..replication_utils import serialize_cart_data, serialize_many_cart_items
from param_classes.accounts.account_replication import ReplicateAccountCreationParams

User = get_user_model()

class AccountReplicator:
    """
    Replicates user's accounts between all "subscribed" microservices.
    """
    def __init__(self):
        self.base_routing_key_name = 'users.accounts'

    @staticmethod
    def __serialize_users_data(user: User) -> Dict[str, Any]:
        user_serializer = UserReplicationSerializer(instance=user)
        users_data = user_serializer.data
        users_data["original_id"] = users_data.pop("id")
        return users_data

    @staticmethod
    def __serialize_cart_data(cart: Cart) -> Dict[str, Any]:
        return serialize_cart_data(cart)

    @staticmethod
    def __serialize_cart_item_data(cart_items: List[CartItem]) -> List[Dict[str, Any]]:
        return serialize_many_cart_items(cart_items)

    def replicate_account_creation(self, params: ReplicateAccountCreationParams) -> None:
        routing_key = self.base_routing_key_name + '.create.one'
        # Serialize User's data
        users_data = self.__serialize_users_data(params.user)
        # Serialize Cart's data
        carts_data = self.__serialize_cart_data(params.cart)
        # Serialize Cart items' data
        cart_items_data = None
        if params.cart_items:
            cart_items_data = self.__serialize_cart_item_data(params.cart_items)

        perform_data_replication.send(
            routing_key, {"user": users_data, "cart": carts_data, "cart_items": cart_items_data},
        )

    def replicate_account_update(self, user: User) -> None:
        routing_key = self.base_routing_key_name + '.update.one'
        users_data = self.__serialize_users_data(user)

        perform_data_replication.send(routing_key, users_data)
