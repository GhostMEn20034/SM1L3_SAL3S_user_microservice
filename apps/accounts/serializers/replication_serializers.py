"""
Serializers to extract data for the replication
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserReplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', )
