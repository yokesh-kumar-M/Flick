from rest_framework import serializers
from .models import FlickUser, WatchHistory, UserWatchlist, GenreStats
import re


def validate_password_strength(value):
    """Shared password validation: requires uppercase + digit."""
    if not re.search(r'[A-Z]', value):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[0-9]', value):
        raise serializers.ValidationError("Password must contain at least one digit.")
    return value


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    display_name = serializers.CharField(max_length=255, required=False, default='')

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        if FlickUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if FlickUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate_password(self, value):
        return validate_password_strength(value)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    avatar_display = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()

    class Meta:
        model = FlickUser
        fields = [
            'id', 'username', 'email', 'display_name', 'bio',
            'avatar_url', 'avatar_display', 'initials',
            'is_admin', 'is_active', 'has_super_access', 'favorite_genre',
            'total_watch_time', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_avatar_display(self, obj):
        return obj.get_avatar_display()

    def get_initials(self, obj):
        return obj.get_initials()


class UserProfileUpdateSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=255, required=False)
    email = serializers.EmailField(required=False)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    favorite_genre = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_email(self, value):
        # Uniqueness check done in view with user exclusion
        return value


class WatchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchHistory
        fields = [
            'id', 'user_id', 'movie_id', 'movie_title', 'movie_poster',
            'progress', 'duration', 'last_position', 'watched_at',
        ]
        read_only_fields = ['id', 'watched_at']


class GenreStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreStats
        fields = ['genre', 'watch_count', 'total_minutes']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def validate_new_password(self, value):
        return validate_password_strength(value)


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWatchlist
        fields = ['id', 'user_id', 'movie_id', 'movie_title', 'movie_slug',
                  'movie_poster', 'added_at']
        read_only_fields = ['id', 'user_id', 'added_at']
