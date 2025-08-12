from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CrmNotification(models.Model):
    LEVELS = (
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crm_notifications", verbose_name="Получатель")
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default="")
    level = models.CharField(max_length=20, choices=LEVELS, default="info")
    meta = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "crm"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.level}] {self.title} -> {self.user_id}"
