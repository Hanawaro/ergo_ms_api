from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Organization(models.Model):
    """Организация в CRM"""
    
    VISIBILITY_CHOICES = [
        ('private', 'private'),
        ('by_invite', 'by_invite'),
    ]
    ROLE_CHOICES = [
        ('member', 'member'),
        ('viewer', 'viewer'),
    ]
    STATUS_CHOICES = [
        ('active', 'active'),
        ('archived', 'archived'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название организации')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Слаг')
    description = models.TextField(blank=True, verbose_name='Описание')
    logo_url = models.URLField(blank=True, verbose_name='Логотип')
    industry = models.CharField(max_length=255, blank=True, verbose_name='Отрасль')
    website = models.URLField(blank=True, verbose_name='Сайт')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=50, blank=True, verbose_name='Телефон')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')
    timezone = models.CharField(max_length=50, blank=True, verbose_name='Часовой пояс')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    billing_name = models.CharField(max_length=255, blank=True, verbose_name='Плательщик')
    billing_vat = models.CharField(max_length=50, blank=True, verbose_name='НДС')
    billing_address = models.CharField(max_length=255, blank=True, verbose_name='Адрес для счетов')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations', verbose_name='Владелец')
    members = models.ManyToManyField(User, through='OrganizationMember', related_name='organizations', through_fields=('organization', 'user'), verbose_name='Участники')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='by_invite', verbose_name='Видимость')
    default_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль по умолчанию')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)