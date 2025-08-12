from rest_framework import serializers
from django.contrib.auth import get_user_model

from src.modules.crm.entities.task_comments.models import TaskComment
from src.modules.crm.entities.tasks.models import Task
from src.modules.crm.entities.users.serializers import CRMUserSerializer

User = get_user_model()

class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария к задаче"""
    author = CRMUserSerializer(read_only=True)
    # принимаем task_id для создания
    task_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = TaskComment
        fields = ['id', 'task_id', 'content', 'author', 'created_at', 'updated_at']

    def validate_task_id(self, value):
        if not Task.objects.filter(id=value).exists():
            raise serializers.ValidationError("Задача не найдена")
        return value

    def create(self, validated_data):
        """
        Создаём комментарий через ViewSet /crm/task-comments/:
        ожидаем task_id и контент; автора берём из request.user
        """
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Требуется аутентификация")

        task_id = validated_data.pop('task_id', None)
        if not task_id:
            raise serializers.ValidationError({"task_id": "Это поле обязательно"})

        # можно сразу через task_id без select
        return TaskComment.objects.create(author=user, task_id=task_id, **validated_data)
