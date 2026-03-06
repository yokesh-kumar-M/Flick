from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('access_approved', 'Access Approved'),
        ('access_denied', 'Access Denied'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('new_content', 'New Content'),
        ('new_review', 'New Review'),
        ('review_liked', 'Review Liked'),
        ('recommendation', 'Recommendation'),
        ('watchlist', 'Watchlist'),
        ('welcome', 'Welcome'),
        ('system', 'System'),
        ('info', 'Info'),
    ]

    user_id = models.IntegerField(db_index=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, default='')
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → User {self.user_id}"
