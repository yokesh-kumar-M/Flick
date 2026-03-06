from django.contrib import admin
from .models import AccessRequest, AccessGrant

@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'movie_id', 'movie_title', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['username', 'movie_title']

@admin.register(AccessGrant)
class AccessGrantAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie_id', 'access_code', 'is_active', 'granted_at', 'expires_at']
    list_filter = ['is_active']
