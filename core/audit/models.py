from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('user_created', 'User Created'),
        ('user_deleted', 'User Deleted'),
        ('user_deactivated', 'User Deactivated'),
        ('user_activated', 'User Activated'),
        ('role_changed', 'Role Changed'),
        ('kindergarten_created', 'Kindergarten Created'),
        ('kindergarten_deleted', 'Kindergarten Deleted'),
        ('admin_attached', 'Admin Attached to Kindergarten'),
        ('admin_detached', 'Admin Detached from Kindergarten'),
        ('credentials_sent', 'Credentials Sent'),
        ('other', 'Other'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.actor} — {self.action} on {self.target_model}:{self.target_id}"
