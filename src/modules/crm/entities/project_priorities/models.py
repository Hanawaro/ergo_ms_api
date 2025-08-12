from django.db import models

class ProjectPriority(models.Model):
    """Приоритеты проектов"""

    name = models.CharField(max_length=100, verbose_name='Название приоритета')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код приоритета')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    level = models.IntegerField(default=1, verbose_name='Уровень приоритета')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Приоритет проекта'
        verbose_name_plural = 'Приоритеты проектов'
        ordering = ['level', 'name']

    def __str__(self):
        return self.name