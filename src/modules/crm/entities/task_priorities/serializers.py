from rest_framework import serializers

from src.modules.crm.entities.task_priorities.models import TaskPriority

class TaskPrioritySerializer(serializers.ModelSerializer):
    """Сериализатор приоритетов задач"""

    class Meta:
        model = TaskPriority
        fields = ['id', 'name', 'code', 'description', 'color', 'level', 'is_active', 'is_default', 'created_at',
                  'updated_at']
        read_only_fields = ['created_at', 'updated_at']