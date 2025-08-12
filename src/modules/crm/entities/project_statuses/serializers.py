from rest_framework import serializers

from src.modules.crm.entities.project_statuses.models import ProjectStatus


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов проектов"""

    class Meta:
        model = ProjectStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']