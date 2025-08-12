from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from src.modules.crm.entities.crm_notifications.models import CrmNotification
from src.modules.crm.entities.crm_notifications.serializers import CrmNotificationSerializer

class CrmNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /crm/notifications/  (GET, list)
    /crm/notifications/<id>/ (GET, retrieve)
    /crm/notifications/<id>/mark_read/ (POST)
    /crm/notifications/mark_all_read/ (POST)
    """
    serializer_class = CrmNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = CrmNotification.objects.filter(user=self.request.user)
        unread_only = self.request.query_params.get("unread_only")
        if unread_only in ("1", "true", "True"):
            qs = qs.filter(is_read=False)
        return qs

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        if not notif.is_read:
            notif.is_read = True
            notif.read_at = timezone.now()
            notif.save(update_fields=["is_read", "read_at"])
        return Response(self.get_serializer(notif).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        CrmNotification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
        return Response(status=status.HTTP_204_NO_CONTENT)
