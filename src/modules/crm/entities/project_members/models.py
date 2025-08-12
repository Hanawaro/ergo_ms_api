from django.db import models
from django.contrib.auth import get_user_model

from src.modules.crm.entities.projects.models import Project

User = get_user_model()

class ProjectMember(models.Model):
    """Участник проекта"""

    ROLE_CHOICES = [
        ('member', 'Участник'),
        ('lead', 'Ведущий'),
        ('observer', 'Наблюдатель'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проектов'
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.project.name}"