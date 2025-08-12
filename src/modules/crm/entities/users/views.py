from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from src.modules.crm.entities.users.serializers import CRMUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для получения пользователей (только чтение)"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = CRMUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'first_name', 'last_name']
    ordering = ['first_name', 'last_name', 'username']