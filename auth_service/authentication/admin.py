from django.contrib import admin
from .models import FlickUser, WatchHistory, GenreStats


@admin.register(FlickUser)
class FlickUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'display_name', 'is_admin', 'is_active', 'created_at']
    list_filter = ['is_admin', 'is_active']
    search_fields = ['username', 'email']


@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie_id', 'movie_title', 'progress', 'watched_at']
    list_filter = ['progress']


@admin.register(GenreStats)
class GenreStatsAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'genre', 'watch_count', 'total_minutes']
