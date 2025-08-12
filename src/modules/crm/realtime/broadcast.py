from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from src.modules.crm.entities.crm_notifications.serializers import CrmNotificationSerializer


def broadcast_comment(task_id: int, action: str, payload: dict):
    """
    action: 'created' | 'updated' | 'deleted'
    payload: сериализованные данные комментария (или {'id': ...} для deleted)
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f"task_{task_id}",
        {
            "type": "comment_event",
            "event": f"comment.{action}",
            "payload": payload,
        }
    )

def broadcast_notification(notification):
    """
    Отправляет конкретное уведомление его получателю по группе user_<id>.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    payload = CrmNotificationSerializer(notification).data
    async_to_sync(channel_layer.group_send)(
        f"user_{notification.user_id}",
        {
            "type": "notification_event",
            "event": "notification.created",
            "payload": payload,
        }
    )