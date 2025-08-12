from django.db import models
from django.conf import settings

from src.modules.crm.entities.organizations.models import Organization

class OrganizationMember(models.Model):
    """Участник организации"""

    ROLE_CHOICES = [
        ('owner', 'owner'),
        ('admin', 'admin'),
        ('member', 'member'),
        ('viewer', 'viewer'),
    ]
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
        ('revoked', 'revoked'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Роль')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='organization_invites_sent',
        verbose_name='Кем приглашён',
    )
    invited_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата приглашения')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата ответа')

    class Meta:
        app_label = 'crm'
        verbose_name = 'Участник организации'
        verbose_name_plural = 'Участники организаций'
        unique_together = ['organization', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name}"