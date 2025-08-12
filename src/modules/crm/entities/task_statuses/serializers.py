from rest_framework import serializers

from src.modules.crm.entities.task_statuses.models import TaskStatus

class TaskStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статусов задач"""

    class Meta:
        model = TaskStatus
        fields = ['id', 'name', 'code', 'description', 'color', 'order', 'is_active', 'is_default', 'is_final',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']