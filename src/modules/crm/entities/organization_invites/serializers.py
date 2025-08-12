from rest_framework import serializers

from src.modules.crm.entities.organization_invites.models import OrganizationInvite
from src.modules.crm.entities.organizations.serializers import OrganizationSerializer
from src.modules.crm.entities.users.serializers import CRMUserSerializer

class OrganizationInviteSerializer(serializers.ModelSerializer):
    """Сериализатор приглашения"""
    
    organization = OrganizationSerializer(read_only=True)
    invited_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = OrganizationInvite
        fields = [
            'id', 'organization', 'email', 'role', 'token',
            'expires_at', 'status', 'invited_by', 'created_at'
        ]
        read_only_fields = ['token', 'status', 'invited_by', 'created_at', 'organization']