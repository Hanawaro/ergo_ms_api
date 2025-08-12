from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.core.utils.mixins import SwaggerSafeMixin
from src.modules.crm.entities.projects.models import Project
from src.modules.crm.entities.task_comments.serializers import TaskCommentSerializer
from src.modules.crm.entities.task_statuses.models import TaskStatus
from src.modules.crm.entities.tasks.models import Task
from src.modules.crm.entities.tasks.serializers import TaskListSerializer, TaskCalendarSerializer, TaskKanbanSerializer, \
    TaskSerializer
from src.modules.crm.entities.time_logs.serializers import TimeLogSerializer


class TaskViewSet(SwaggerSafeMixin, viewsets.ModelViewSet):
    """ViewSet для управления задачами"""
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project', 'assignee', 'creator', 'parent']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority', 'kanban_order']
    ordering = ['kanban_order', '-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'calendar':
            return TaskCalendarSerializer
        elif self.action == 'kanban':
            return TaskKanbanSerializer
        return TaskSerializer

    def get_queryset(self):
        if self.is_swagger_fake_view():
            return Task.objects.none()

        user = self.get_safe_user()
        if not user:
            return Task.objects.none()

        queryset = super().get_queryset()

        # Ограничиваем задачи организациями, где пользователь владелец
        # или принятый участник
        queryset = queryset.filter(
            Q(organization__owner=user) |
            Q(organization__memberships__user=user, organization__memberships__status='accepted')
        )

        # Параметр "Мои задачи"
        my_tasks = self.request.query_params.get('my_tasks', None)

        if my_tasks and my_tasks.lower() == 'true':
            # Только мои задачи - только задачи, где я исполнитель
            queryset = queryset.filter(assignee=user).distinct()
        else:
            # Показываем все задачи из проектов, в которых пользователь участвует
            queryset = queryset.filter(
                Q(project__owner=user) |
                Q(project__manager=user) |
                Q(project__team_members=user) |
                Q(assignee=user) |
                Q(creator=user)
            ).distinct()

        # Фильтр по дате для календаря
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date and end_date:
            queryset = queryset.filter(
                Q(start_date__range=[start_date, end_date]) |
                Q(due_date__range=[start_date, end_date])
            )

        return queryset

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Получить задачи для календаря"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            # По умолчанию текущий месяц
            now = timezone.now()
            start_date = now.replace(day=1).date()
            end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)

        tasks = self.get_queryset().filter(
            Q(start_date__range=[start_date, end_date]) |
            Q(due_date__range=[start_date, end_date])
        )

        serializer = TaskCalendarSerializer(tasks, many=True)

        # Преобразуем в формат для календаря
        events = []
        for task in serializer.data:
            # Событие начала задачи
            if task['start_date']:
                events.append({
                    'id': f"start_{task['id']}",
                    'title': f"▶ {task['title']}",
                    'start': task['start_date'],
                    'backgroundColor': self.get_task_color(task['priority'], task['status']),
                    'task_id': task['id'],
                    'type': 'start',
                    'task_data': task
                })

            # Событие срока выполнения
            if task['due_date']:
                events.append({
                    'id': f"due_{task['id']}",
                    'title': f"⏰ {task['title']}",
                    'start': task['due_date'],
                    'backgroundColor': self.get_due_color(task['priority'], task['status']),
                    'task_id': task['id'],
                    'type': 'due',
                    'task_data': task
                })

        return Response({'events': events})

    def get_task_color(self, priority, status):
        """Получить цвет задачи для календаря"""
        if status == 'done':
            return '#28a745'  # Зеленый для выполненных
        elif status == 'cancelled':
            return '#6c757d'  # Серый для отмененных
        elif priority == 'urgent':
            return '#dc3545'  # Красный для срочных
        elif priority == 'high':
            return '#fd7e14'  # Оранжевый для высокого приоритета
        elif priority == 'medium':
            return '#007bff'  # Синий для среднего приоритета
        else:
            return '#6f42c1'  # Фиолетовый для низкого приоритета

    def get_due_color(self, priority, status):
        """Получить цвет срока выполнения"""
        if status == 'done':
            return '#28a745'
        elif priority == 'urgent':
            return '#dc3545'
        else:
            return '#ffc107'  # Желтый для сроков

    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Получить задачи для канбан доски"""
        project_id = request.query_params.get('project_id')
        priority = request.query_params.get('priority')
        assignee = request.query_params.get('assignee')
        ordering = request.query_params.get('ordering', 'kanban_order')

        queryset = self.get_queryset()

        # Применяем фильтры
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        if priority:
            queryset = queryset.filter(priority=priority)

        if assignee:
            queryset = queryset.filter(assignee_id=assignee)

        # Применяем сортировку
        ordering_fields = {
            'kanban_order': ['kanban_order', '-created_at'],
            '-created_at': ['-created_at'],
            'created_at': ['created_at'],
            'due_date': ['due_date', '-created_at'],
            '-due_date': ['-due_date', '-created_at'],
            'priority': ['priority_ref__level', 'priority', '-created_at'],
            '-priority': ['-priority_ref__level', '-priority', '-created_at'],
            'assignee': ['assignee__first_name', 'assignee__last_name', '-created_at'],
            '-assignee': ['-assignee__first_name', '-assignee__last_name', '-created_at']
        }

        # Применяем сортировку с fallback
        ordering_list = ordering_fields.get(ordering, ['kanban_order', '-created_at'])
        queryset = queryset.order_by(*ordering_list)

        # Получаем все активные статусы задач
        try:
            # Используем все активные статусы
            kanban_statuses = TaskStatus.objects.filter(is_active=True).order_by('order', 'name')
        except Exception:
            # Fallback: используем старые статусы
            kanban_statuses = []

        # Группируем по статусам
        kanban_data = {}

        if kanban_statuses:
            # Используем динамические статусы
            for status in kanban_statuses:
                tasks = queryset.filter(status=status.code)
                serializer = TaskKanbanSerializer(tasks, many=True)
                kanban_data[status.code] = serializer.data
        else:
            # Fallback к старым жестко заданным статусам
            fallback_statuses = ['todo', 'in_progress', 'review', 'done']
            for status_key in fallback_statuses:
                tasks = queryset.filter(status=status_key)
                serializer = TaskKanbanSerializer(tasks, many=True)
                kanban_data[status_key] = serializer.data

        return Response(kanban_data)

    @action(detail=True, methods=['post'])
    def update_kanban_order(self, request, pk=None):
        """Обновить порядок задач в канбан"""
        task = self.get_object()
        new_order = request.data.get('order')
        new_status = request.data.get('status')

        if new_order is not None:
            task.kanban_order = new_order

        if new_status:
            # Проверяем существование статуса в новой системе
            try:
                status_obj = TaskStatus.objects.get(code=new_status, is_active=True)
                task.status = new_status
                task.status_ref = status_obj

                # Если задача помечена как выполненная
                if status_obj.is_final and not task.completed_at:
                    task.completed_at = timezone.now()
                elif not status_obj.is_final:
                    task.completed_at = None

            except TaskStatus.DoesNotExist:
                # Fallback: проверяем по старым choices
                if new_status in dict(Task.TASK_STATUS_CHOICES):
                    task.status = new_status

                    # Для обратной совместимости
                    if new_status == 'done' and not task.completed_at:
                        task.completed_at = timezone.now()
                    elif new_status != 'done':
                        task.completed_at = None
                else:
                    return Response({'error': f'Неверный статус: {new_status}'}, status=status.HTTP_400_BAD_REQUEST)

        task.save()
        return Response({'message': 'Порядок задач обновлен'})

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус задачи"""
        task = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Task.TASK_STATUS_CHOICES):
            return Response({'error': 'Неверный статус'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status

        if new_status == 'done':
            task.completed_at = timezone.now()
        elif new_status == 'in_progress' and not task.start_date:
            task.start_date = timezone.now()

        task.save()
        return Response({'message': 'Статус задачи изменен'})

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Добавить комментарий к задаче"""
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_time_log(self, request, pk=None):
        """Добавить учет времени"""
        task = self.get_object()
        serializer = TimeLogSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_from_calendar(self, request):
        """Создать задачу из календаря"""
        data = request.data.copy()

        # Если не указан проект, пытаемся найти активный проект пользователя
        if not data.get('project_id'):
            active_project = Project.objects.filter(
                Q(owner=request.user) | Q(manager=request.user),
                status='active'
            ).first()

            if active_project:
                data['project_id'] = active_project.id
            else:
                return Response(
                    {'error': 'Необходимо указать проект'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = TaskSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
