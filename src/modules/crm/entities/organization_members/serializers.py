from rest_framework import serializers

from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.users.serializers import CRMUserSerializer

class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника организации"""
    
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    invited_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'user_id', 'role', 'status', 'invited_by', 'invited_at', 'responded_at']
        read_only_fields = ['invited_by', 'invited_at', 'responded_at']