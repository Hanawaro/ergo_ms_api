from rest_framework import serializers

from src.modules.crm.entities.time_logs.models import TimeLog
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class TimeLogSerializer(serializers.ModelSerializer):
    """Сериализатор учета времени"""
    user = CRMUserSerializer(read_only=True)

    class Meta:
        model = TimeLog
        fields = ['id', 'description', 'hours', 'date', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)