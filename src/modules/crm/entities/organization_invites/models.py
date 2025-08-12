from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
import secrets

from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.organizations.models import Organization

User = get_user_model()

class OrganizationInvite(models.Model):
    """Приглашение в организацию"""

    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
        ('expired', 'expired'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invites')
    email = models.EmailField(verbose_name='Email')
    role = models.CharField(
        max_length=20,
        choices=OrganizationMember.ROLE_CHOICES,
        default='member',
        verbose_name='Роль'
    )
    token = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Истекает')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_invites', verbose_name='Пригласивший')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата ответа')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Приглашение в организацию'
        verbose_name_plural = 'Приглашения в организации'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(16)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} -> {self.organization.name}"