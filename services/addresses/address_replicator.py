from typing import Dict, Any
from django.conf import settings

from apps.addresses.serializers import AddressReplicationSerializer
from apps.addresses.models import Address
from apps.core.tasks import perform_data_topic_replication


class AddressReplicator:
    """
    Replicates user's addresses between all "subscribed" microservices.
    """
    def __init__(self):
        self.base_routing_key_name = 'users.addresses'
        self.exchange_name = settings.USERS_DATA_CRUD_EXCHANGE_TOPIC_NAME

    @staticmethod
    def __serialize_address(address: Address) -> Dict[str, Any]:
        address_serializer = AddressReplicationSerializer(instance=address)
        address_data = address_serializer.data
        address_data["original_id"] = address_data.pop("id")
        return address_data

    def replicate_address_creation(self, address: Address) -> None:
        routing_key = self.base_routing_key_name + '.create.one'
        address_data = self.__serialize_address(address)
        perform_data_topic_replication.send(self.exchange_name, routing_key, address_data)

    def replicate_address_update(self, address: Address) -> None:
        routing_key = self.base_routing_key_name + '.update.one'
        address_data = self.__serialize_address(address)
        perform_data_topic_replication.send(self.exchange_name, routing_key, address_data)

    def replicate_address_delete(self, address_id: int) -> None:
        routing_key = self.base_routing_key_name + '.delete.one'
        perform_data_topic_replication.send(
            self.exchange_name, routing_key,
            {"address_id": address_id}
        )
