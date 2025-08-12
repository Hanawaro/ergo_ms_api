from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from src.modules.crm.entities.organization_members.models import OrganizationMember
from src.modules.crm.entities.organizations.models import Organization
from src.modules.crm.entities.organizations.serializers import OrganizationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet для управления организациями"""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        user = self.request.user
        return Organization.objects.filter(
            Q(owner=user) | Q(memberships__user=user, memberships__status='accepted')
        ).distinct()

    def perform_create(self, serializer):
        organization = serializer.save(owner=self.request.user)
        OrganizationMember.objects.create(
            organization=organization,
            user=self.request.user,
            role='owner',
            status='accepted',
            invited_by=self.request.user,
            invited_at=timezone.now(),
            responded_at=timezone.now()
        )

    def destroy(self, request, *args, **kwargs):
        organization = self.get_object()
        if organization.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Пригласить пользователя в организацию"""
        
        organization = self.get_object()
        # Проверяем права: только владелец или администратор
        if not (
            organization.owner == request.user or
            OrganizationMember.objects.filter(
                organization=organization,
                user=request.user,
                role__in=['owner', 'admin'],
                status='accepted'
            ).exists()
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', organization.default_role)

        if not email:
            return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if role not in dict(OrganizationMember.ROLE_CHOICES) or role == 'owner':
            return Response({'error': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        invite = OrganizationInvite.objects.create(
            organization=organization,
            email=email,
            role=role,
            invited_by=request.user,
        )
        return Response({'token': invite.token, 'status': invite.status}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Список участников организации"""

        organization = self.get_object()
        if not (organization.owner == request.user or OrganizationMember.objects.filter(organization=organization, user=request.user, role__in=['owner', 'admin'], status='accepted').exists()):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = OrganizationMemberSerializer(organization.memberships.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch', 'delete'], url_path='members/(?P<user_id>[^/.]+)')
    def manage_member(self, request, pk=None, user_id=None):
        """Изменение роли или удаление участника"""

        organization = self.get_object()
        if not (organization.owner == request.user or OrganizationMember.objects.filter(organization=organization, user=request.user, role__in=['owner', 'admin'], status='accepted').exists()):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            member = OrganizationMember.objects.get(organization=organization, user_id=user_id)
        except OrganizationMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            role = request.data.get('role')
            if role not in dict(OrganizationMember.ROLE_CHOICES) or role == 'owner':
                return Response({'error': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)
            member.role = role
            member.save()
            return Response(OrganizationMemberSerializer(member).data)

        if member.role == 'owner':
            return Response({'error': 'cannot remove owner'}, status=status.HTTP_400_BAD_REQUEST)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
