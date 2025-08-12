from django.db import models

from django.contrib.auth import get_user_model

from src.modules.crm.entities.tasks.models import Task

User = get_user_model()

class TaskAttachment(models.Model):
    """Прикрепленный файл к задаче"""
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments', verbose_name='Задача')
    file = models.FileField(upload_to='task_attachments/', verbose_name='Файл')
    filename = models.CharField(max_length=255, verbose_name='Имя файла')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_attachments', verbose_name='Загрузил')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Прикрепленный файл'
        verbose_name_plural = 'Прикрепленные файлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.filename