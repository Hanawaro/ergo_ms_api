from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin
from src.modules.crm.entities.time_logs.models import TimeLog
from src.modules.crm.entities.time_logs.serializers import TimeLogSerializer


class TimeLogViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для учета времени"""
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task', 'user', 'date']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return TimeLog.objects.none()

        user = self.get_safe_user()
        if not user:
            return TimeLog.objects.none()

        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset

    @action(detail=False, methods=['get'])
    def my_time_logs(self, request):
        """Получить мои записи времени"""
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)