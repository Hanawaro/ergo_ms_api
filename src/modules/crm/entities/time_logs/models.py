from django.db import models

from django.contrib.auth import get_user_model

from src.modules.crm.entities.tasks.models import Task

User = get_user_model()

class TimeLog(models.Model):
    """Учет времени по задаче"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs', verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_logs', verbose_name='Пользователь')
    description = models.TextField(blank=True, verbose_name='Описание работы')
    hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Количество часов')
    date = models.DateField(verbose_name='Дата работы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Учет времени'
        verbose_name_plural = 'Учет времени'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.task.title} - {self.hours}ч"