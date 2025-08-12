from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.modules.crm.entities.project_statuses.models import ProjectStatus
from src.modules.crm.entities.project_statuses.serializers import ProjectStatusSerializer


class ProjectStatusViewSet(viewsets.ModelViewSet):
    """ViewSet для управления статусами проектов"""
    queryset = ProjectStatus.objects.filter(is_active=True)
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['order', 'name', 'created_at']
    ordering = ['order', 'name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные статусы"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить статус по умолчанию"""
        try:
            default_status = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_status)
            return Response(serializer.data)
        except ProjectStatus.DoesNotExist:
            return Response({'error': 'Статус по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)
