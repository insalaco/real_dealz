from django.db import models
from django.utils import timezone

class InboundEmail(models.Model):
    """
    Represents a single email received via Mailgun (polled from the 'stored' events API).
    """

    message_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Mailgun message ID"
    )

    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    subject = models.TextField(null=True, blank=True)

    body_plain = models.TextField(null=True, blank=True)
    body_html = models.TextField(null=True, blank=True)

    raw_mime = models.TextField(null=True, blank=True)

    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Raw Mailgun event JSON or headers"
    )

    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    is_processed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.subject or '(No Subject)'} from {self.sender}"
