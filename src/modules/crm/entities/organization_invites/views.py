from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from src.modules.crm.entities.organization_invites.models import OrganizationInvite
from src.modules.crm.entities.organization_invites.serializers import OrganizationInviteSerializer
from src.modules.crm.entities.organization_members.models import OrganizationMember


class OrganizationInviteViewSet(viewsets.ViewSet):
    """ViewSet для приглашений в организации"""
    
    permission_classes = [IsAuthenticated]

    def list(self, request):
        invites = OrganizationInvite.objects.filter(
            email=request.user.email, status='pending'
        ).filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
        serializer = OrganizationInviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def accept(self, request):
        token = request.data.get('token')
        try:
            invite = OrganizationInvite.objects.get(token=token, email=request.user.email)
        except OrganizationInvite.DoesNotExist:
            return Response({'error': 'Инвайт не найден'}, status=status.HTTP_404_NOT_FOUND)
        if invite.expires_at and invite.expires_at < timezone.now():
            invite.status = 'expired'
            invite.save()
            return Response({'error': 'Инвайт просрочен'}, status=status.HTTP_410_GONE)
        invite.status = 'accepted'
        invite.responded_at = timezone.now()
        invite.save()
        OrganizationMember.objects.create(
            organization=invite.organization,
            user=request.user,
            role=invite.role,
            status='accepted',
            invited_by=invite.invited_by,
            invited_at=invite.created_at,
            responded_at=timezone.now()
        )
        return Response({'status': 'accepted'})

    @action(detail=False, methods=['post'])
    def decline(self, request):
        token = request.data.get('token')
        try:
            invite = OrganizationInvite.objects.get(token=token, email=request.user.email)
        except OrganizationInvite.DoesNotExist:
            return Response({'error': 'Инвайт не найден'}, status=status.HTTP_404_NOT_FOUND)
        invite.status = 'declined'
        invite.responded_at = timezone.now()
        invite.save()
        return Response({'status': 'declined'})

