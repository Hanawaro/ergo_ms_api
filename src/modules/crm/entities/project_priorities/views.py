from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.modules.crm.entities.project_priorities.models import ProjectPriority
from src.modules.crm.entities.project_priorities.serializers import ProjectPrioritySerializer


class ProjectPriorityViewSet(viewsets.ModelViewSet):
    """ViewSet для управления приоритетами проектов"""
    queryset = ProjectPriority.objects.filter(is_active=True)
    serializer_class = ProjectPrioritySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['level', 'name']

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить только активные приоритеты"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def default(self, request):
        """Получить приоритет по умолчанию"""
        try:
            default_priority = self.get_queryset().get(is_default=True)
            serializer = self.get_serializer(default_priority)
            return Response(serializer.data)
        except ProjectPriority.DoesNotExist:
            return Response({'error': 'Приоритет по умолчанию не найден'}, status=status.HTTP_404_NOT_FOUND)