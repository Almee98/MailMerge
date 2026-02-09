from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Campaign(models.Model):
    # Created but not scheduled or sending yet.
    STATE_DRAFT = 'draft'
    # Scheduled for a future send time.
    STATE_SCHEDULED = 'scheduled'
    # Actively sending messages to recipients.
    STATE_SENDING = 'sending'
    # All recipients attempted (may include per-recipient failures).
    STATE_COMPLETED = 'completed'
    # Campaign-level failure that prevents completion.
    STATE_FAILED = 'failed'

    STATE_CHOICES = [
        (STATE_DRAFT, 'Draft'),
        (STATE_SCHEDULED, 'Scheduled'),
        (STATE_SENDING, 'Sending'),
        (STATE_COMPLETED, 'Completed'),
        (STATE_FAILED, 'Failed'),
    ]

    # Internal label for dashboards and admin views.
    name = models.CharField(max_length=255)
    # Subject line; can include merge fields like {{first_name}}.
    subject = models.CharField(max_length=255)
    # Sender address used for outbound messages.
    from_email = models.EmailField()
    # Email body template with merge fields like {{first_name}}.
    template = models.TextField()
    # Campaign lifecycle state (draft -> completed).
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_DRAFT)
    # Optional scheduled send time for queued campaigns.
    scheduled_for = models.DateTimeField(null=True, blank=True)
    # Owner of the campaign for access control/auditing.
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Recipient(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.EmailField()
    data = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campaign', 'email')

    def __str__(self):
        return self.email


class SendAttempt(models.Model):
    STATUS_QUEUED = 'queued'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_QUEUED, 'Queued'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='send_attempts')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='send_attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    provider_message_id = models.CharField(max_length=200, null=True, blank=True)
    error = models.TextField(blank=True)
    attempt_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.recipient.email} - {self.status}"


class Suppression(models.Model):
    REASON_UNSUBSCRIBED = 'unsubscribed'
    REASON_BOUNCED = 'bounced'
    REASON_COMPLAINED = 'complained'
    REASON_CHOICES = [
        (REASON_UNSUBSCRIBED, 'Unsubscribed'),
        (REASON_BOUNCED, 'Bounced'),
        (REASON_COMPLAINED, 'Complained'),
    ]

    email = models.EmailField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='suppressions', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'reason')

    def __str__(self):
        return f"{self.email} - {self.reason}"