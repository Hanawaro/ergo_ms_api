from rest_framework import serializers

from src.modules.crm.entities.organization_members.serializers import OrganizationMemberSerializer
from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class OrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор организации"""
    
    owner = CRMUserSerializer(read_only=True)
    memberships = OrganizationMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo_url', 'industry', 'website',
            'email', 'phone', 'country', 'timezone', 'address',
            'billing_name', 'billing_vat', 'billing_address',
            'owner', 'memberships', 'visibility', 'default_role', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'owner', 'created_at', 'updated_at']