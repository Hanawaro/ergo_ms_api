from channels.generic.websocket import AsyncJsonWebsocketConsumer

class TaskCommentsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('hehjeasfdkjl;sjfkldsjfkldsjfkldsjflksd', 2)
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]
        self.room = f"task_{self.task_id}"
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

    async def comment_event(self, event):
        await self.send_json({
            "event": event["event"],
            "payload": event["payload"],
        })

class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('hehjeasfdkjl;sjfkldsjfkldsjfkldsjflksd')
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group = f"user_{user_id}"
        print('self.group', self.group)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def notification_event(self, event):
        await self.send_json({
            "event": event["event"],
            "payload": event["payload"],
        })