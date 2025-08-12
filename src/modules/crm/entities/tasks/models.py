from django.db import models

from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.projects.models import Project

from django.contrib.auth import get_user_model

from src.modules.crm.entities.task_priorities.models import TaskPriority
from src.modules.crm.entities.task_statuses.models import TaskStatus

User = get_user_model()

class Task(models.Model):
    """Задача"""
    
    # Обратная совместимость - старые choices остаются как fallback
    TASK_STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    title = models.CharField(max_length=255, verbose_name='Название задачи')
    description = models.TextField(blank=True, verbose_name='Описание')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Проект')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True, verbose_name='Организация')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name='Исполнитель')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='Создатель')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks', verbose_name='Родительская задача')
    # Новые поля с внешними ключами
    status_ref = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='Статус (новый)')
    priority_ref = models.ForeignKey(TaskPriority, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks', verbose_name='Приоритет (новый)')

    # Старые поля для обратной совместимости
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='todo', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Оценка времени (часы)')
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Фактическое время (часы)')
    kanban_order = models.IntegerField(default=0, verbose_name='Порядок в канбан')

    custom_fields = models.JSONField(default=dict, blank=True, verbose_name='Пользовательские поля')  # NEW

    class Meta:
        app_label = 'crm'
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['kanban_order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def current_status(self):
        """Получить текущий статус (приоритет новому полю)"""
        return self.status_ref.code if self.status_ref else self.status

    @property
    def current_priority(self):
        """Получить текущий приоритет (приоритет новому полю)"""
        return self.priority_ref.code if self.priority_ref else self.priority

    @property
    def status_display(self):
        """Получить отображаемое название статуса"""
        return self.status_ref.name if self.status_ref else dict(self.TASK_STATUS_CHOICES).get(self.status, self.status)

    @property
    def priority_display(self):
        """Получить отображаемое название приоритета"""
        return self.priority_ref.name if self.priority_ref else dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)