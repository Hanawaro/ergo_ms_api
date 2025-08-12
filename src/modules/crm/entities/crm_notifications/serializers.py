from rest_framework import serializers
from src.modules.crm.entities.crm_notifications.models import CrmNotification

class CrmNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrmNotification
        fields = [
            "id", "title", "message", "level", "meta",
            "is_read", "read_at", "created_at",
        ]
        read_only_fields = ["id", "created_at", "read_at"]
