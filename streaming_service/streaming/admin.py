from django.contrib import admin
from .models import TranscodeJob, StreamSession

@admin.register(TranscodeJob)
class TranscodeJobAdmin(admin.ModelAdmin):
    list_display = ['movie_id', 'status', 'progress', 'created_at', 'completed_at']
    list_filter = ['status']

@admin.register(StreamSession)
class StreamSessionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie_id', 'quality', 'is_active', 'started_at', 'last_heartbeat']
    list_filter = ['is_active', 'quality']
