from django.db import models


class AccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('revoked', 'Revoked'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('not_required', 'Not Required'),  # For admin/super users
        ('pending', 'Awaiting Payment'),
        ('completed', 'Payment Completed'),
        ('failed', 'Payment Failed'),
    ]

    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=150, default='')
    user_email = models.EmailField(max_length=255, default='')  # For emailing access code
    movie_id = models.IntegerField(db_index=True)
    movie_title = models.CharField(max_length=500, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=255, blank=True, default='')  # Stripe/PayPal transaction ID
    access_code = models.CharField(max_length=50, blank=True, default='')
    code_timestamp = models.CharField(max_length=50, blank=True, default='')
    email_sent = models.BooleanField(default=False)  # Track if access code was emailed
    reason = models.TextField(blank=True, default='')
    admin_note = models.TextField(blank=True, default='')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'access_requests'
        ordering = ['-created_at']
        unique_together = ['user_id', 'movie_id']

    def __str__(self):
        return f"User {self.user_id} → Movie {self.movie_id} [{self.status}]"


class AccessGrant(models.Model):
    """Tracks active access grants for users to movies."""
    user_id = models.IntegerField(db_index=True)
    movie_id = models.IntegerField(db_index=True)
    access_code = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'access_grants'
        unique_together = ['user_id', 'movie_id']

    def __str__(self):
        return f"Grant: User {self.user_id} → Movie {self.movie_id}"
