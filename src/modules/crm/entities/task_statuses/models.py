from django.db import models

class TaskStatus(models.Model):
    """Статусы задач"""
    
    name = models.CharField(max_length=100, verbose_name='Название статуса')
    code = models.CharField(max_length=50, unique=True, verbose_name='Код статуса')
    description = models.TextField(blank=True, verbose_name='Описание')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Цвет')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')
    is_final = models.BooleanField(default=False, verbose_name='Финальный статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name