from rest_framework import serializers

from src.modules.crm.entities.project_priorities.models import ProjectPriority


class ProjectPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов проектов"""

    class Meta:
        model = ProjectPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at',
                  'updated_at']
        read_only_fields = ['created_at', 'updated_at']