from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CRMUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']