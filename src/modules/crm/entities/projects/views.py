from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin
from src.modules.crm.entities.project_members.models import ProjectMember
from src.modules.crm.entities.project_members.serializers import ProjectMemberSerializer
from src.modules.crm.entities.projects.models import Project
from src.modules.crm.entities.projects.serializers import ProjectListSerializer, ProjectSerializer
from src.modules.crm.entities.tasks.serializers import TaskListSerializer


class ProjectViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для управления проектами"""
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'owner', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Project.objects.none()

        user = self.get_safe_user()
        if not user:
            return Project.objects.none()

        queryset = super().get_queryset()

        # Показываем только проекты организаций, где пользователь является владельцем
        # или принятым участником
        queryset = queryset.filter(
            Q(organization__owner=user) |
            Q(organization__memberships__user=user, organization__memberships__status='accepted')
        ).filter(
            Q(owner=user) |
            Q(manager=user) |
            Q(team_members=user)
        ).distinct()

        # Дополнительный фильтр "Мои проекты" (оставляем для совместимости)
        my_projects = self.request.query_params.get('my_projects', None)
        if my_projects and my_projects.lower() == 'false':
            # Если явно указано false, показываем все доступные проекты
            queryset = super().get_queryset()

        return queryset

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Добавить участника в проект"""
        project = self.get_object()
        serializer = ProjectMemberSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Проверяем, не является ли пользователь уже участником
                user_id = serializer.validated_data['user_id']
                if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
                    return Response({'error': 'Пользователь уже является участником проекта'},
                                    status=status.HTTP_400_BAD_REQUEST)

                member = serializer.save(project=project)

                # Возвращаем полные данные участника
                response_serializer = ProjectMemberSerializer(member)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Удалить участника из проекта"""
        project = self.get_object()
        user_id = request.data.get('user_id')

        try:
            membership = ProjectMember.objects.get(project=project, user_id=user_id)
            membership.delete()
            return Response({'message': 'Участник удален из проекта'})
        except ProjectMember.DoesNotExist:
            return Response({'error': 'Участник не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить задачи проекта"""
        project = self.get_object()
        tasks = project.tasks.all()
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Получить статистику проекта"""
        project = self.get_object()

        total_tasks = project.tasks.count()

        # Завершенные задачи с учетом новой и старой системы статусов
        completed_tasks = project.tasks.filter(
            Q(status_ref__is_final=True, status_ref__is_active=True) | Q(status='done')
        ).count()

        # Задачи в работе с учетом новой системы
        in_progress_tasks = project.tasks.filter(
            Q(status_ref__code='in_progress', status_ref__is_active=True) | Q(status='in_progress')
        ).count()

        # Просроченные задачи - которые не завершены и срок прошел
        overdue_tasks = project.tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(
            Q(status_ref__is_final=True, status_ref__is_active=True) | Q(status='done')
        ).count()

        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'overdue_tasks': overdue_tasks,
            'progress': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        })