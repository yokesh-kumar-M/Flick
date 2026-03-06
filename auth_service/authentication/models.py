from django.db import models
import bcrypt


class FlickUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    has_super_access = models.BooleanField(default=False)  # Unlimited access to all content (granted by admin)
    favorite_genre = models.CharField(max_length=100, blank=True, default='')
    total_watch_time = models.IntegerField(default=0)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flick_users'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def get_avatar_display(self):
        """Return best available avatar URL."""
        if self.avatar:
            return self.avatar.url
        return self.avatar_url or ''

    def get_initials(self):
        name = self.display_name or self.username or 'U'
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[0].upper()


class WatchHistory(models.Model):
    user_id = models.IntegerField(db_index=True)
    movie_id = models.IntegerField(db_index=True)
    movie_title = models.CharField(max_length=500, default='')
    movie_poster = models.URLField(blank=True, default='')
    progress = models.FloatField(default=0)   # 0-100 percentage
    duration = models.IntegerField(default=0)  # total duration in seconds
    last_position = models.IntegerField(default=0)  # last watched position in seconds
    watched_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watch_history'
        ordering = ['-watched_at']
        unique_together = ['user_id', 'movie_id']

    def __str__(self):
        return f"User {self.user_id} - Movie {self.movie_id} ({self.progress}%)"


class UserWatchlist(models.Model):
    """Server-side watchlist for saving movies."""
    user_id = models.IntegerField(db_index=True)
    movie_id = models.IntegerField(db_index=True)
    movie_title = models.CharField(max_length=500, default='')
    movie_slug = models.SlugField(max_length=500, default='')
    movie_poster = models.URLField(blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_watchlist'
        ordering = ['-added_at']
        unique_together = ['user_id', 'movie_id']

    def __str__(self):
        return f"User {self.user_id} - {self.movie_title}"


class GenreStats(models.Model):
    user_id = models.IntegerField(db_index=True)
    genre = models.CharField(max_length=100)
    watch_count = models.IntegerField(default=0)
    total_minutes = models.IntegerField(default=0)

    class Meta:
        db_table = 'genre_stats'
        unique_together = ['user_id', 'genre']
        ordering = ['-watch_count']

    def __str__(self):
        return f"User {self.user_id} - {self.genre}: {self.watch_count}"
