from django.db import models


class TranscodeJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    movie_id = models.IntegerField(db_index=True)
    source_file = models.CharField(max_length=1000)
    output_dir = models.CharField(max_length=1000, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0)
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transcode_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transcode: Movie {self.movie_id} [{self.status}]"


class StreamSession(models.Model):
    user_id = models.IntegerField(db_index=True)
    movie_id = models.IntegerField(db_index=True)
    session_token = models.CharField(max_length=255, unique=True)
    quality = models.CharField(max_length=20, default='auto')
    started_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'stream_sessions'
        ordering = ['-started_at']

    def __str__(self):
        return f"Stream: User {self.user_id} → Movie {self.movie_id}"
