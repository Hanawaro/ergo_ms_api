from django.db import models
from django.core.validators import RegexValidator

class FieldSetting(models.Model):
    """Пользовательское поле для проектов/задач."""

    ENTITY_CHOICES = [
        ('project', 'Проект'),
        ('task', 'Задача'),
    ]

    TYPE_CHOICES = [
        ('text', 'Текст'),
        ('number', 'Число'),
        ('date', 'Дата'),
        ('datetime', 'Дата и время'),
        ('checkbox', 'Чекбокс'),
        ('textarea', 'Текстовая область'),
    ]

    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES, verbose_name='Тип сущности')
    name = models.CharField(max_length=64,validators=[RegexValidator(r'^[a-zA-Z0-9_]+$')],verbose_name='Системное имя')
    label = models.CharField(max_length=128, verbose_name='Название поля')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')
    sort_index = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Настройка поля'
        verbose_name_plural = 'Настройки полей'
        ordering = ['entity_type', 'sort_index', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['entity_type', 'name'],
                name='uniq_field_per_org_entity'
            ),
        ]

    def __str__(self):
        return f"[{self.entity_type}:{self.name} ({self.label})"