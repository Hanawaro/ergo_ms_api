from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.project_priorities.models import ProjectPriority
from src.modules.crm.entities.project_statuses.models import ProjectStatus

User = get_user_model()

class Project(models.Model):
    """Общий проект (не стратегический)"""
    PROJECT_STATUS_CHOICES = [
        ('planning', 'Планирование'),
        ('active', 'Активный'),
        ('on_hold', 'Приостановлен'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]
    name = models.CharField(max_length=255, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='projects', null=True, blank=True, verbose_name='Организация')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects', verbose_name='Владелец проекта')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects', verbose_name='Менеджер проекта')
    team_members = models.ManyToManyField(User, through='ProjectMember', related_name='project_teams', verbose_name='Участники команды')

    # Новые поля с внешними ключами
    status_ref = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Статус (новый)')
    priority_ref = models.ForeignKey(ProjectPriority, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name='Приоритет (новый)')

    # Старые поля для обратной совместимости
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='planning', verbose_name='Статус')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')

    start_date = models.DateField(null=True, blank=True, verbose_name='Дата начала')
    end_date = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет проекта')

    custom_fields = models.JSONField(default=dict, blank=True, verbose_name='Пользовательские поля')  # NEW

    class Meta:
        app_label = 'crm'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

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
        return self.status_ref.name if self.status_ref else dict(self.PROJECT_STATUS_CHOICES).get(self.status, self.status)

    @property
    def priority_display(self):
        """Получить отображаемое название приоритета"""
        return self.priority_ref.name if self.priority_ref else dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)