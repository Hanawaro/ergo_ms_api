from rest_framework import serializers

from src.modules.crm.entities.task_attachments.models import TaskAttachment
from src.modules.crm.entities.users.serializers import CRMUserSerializer


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор прикрепленного файла"""
    uploaded_by = CRMUserSerializer(read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'uploaded_by', 'uploaded_at']

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)