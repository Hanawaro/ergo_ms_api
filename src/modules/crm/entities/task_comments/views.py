from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from src.modules.crm.entities.crm_notifications.models import CrmNotification
from src.modules.crm.entities.task_comments.models import TaskComment
from src.modules.crm.entities.task_comments.serializers import TaskCommentSerializer
from src.modules.crm.realtime.broadcast import broadcast_comment, broadcast_notification

User = get_user_model()

class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев к задачам"""
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs.select_related('author', 'task')

    def perform_create(self, serializer):
        instance: TaskComment = serializer.save()
        data = TaskCommentSerializer(instance, context=self.get_serializer_context()).data
        broadcast_comment(instance.task_id, "created", data)

        notif = CrmNotification.objects.create(
            user_id=data['author']['id'],
            title='Уведомление',
            message='Пользователь оставил комментарий',
            level='info',
            meta={},
        )
        broadcast_notification(notif)

    def perform_update(self, serializer):
        instance: TaskComment = serializer.save()
        data = TaskCommentSerializer(instance, context=self.get_serializer_context()).data
        broadcast_comment(instance.task_id, "updated", data)

    def perform_destroy(self, instance):
        task_id = instance.task_id
        comment_id = instance.id
        super().perform_destroy(instance)
        broadcast_comment(task_id, "deleted", {"id": comment_id})
