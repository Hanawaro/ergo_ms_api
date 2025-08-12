from rest_framework import serializers

from src.modules.crm.entities.project_members.models import ProjectMember
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Сериализатор участника проекта"""
    user = CRMUserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']