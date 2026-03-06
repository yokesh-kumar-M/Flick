from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, blank=True, default='🎬')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        ordering = ['order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        db_table = 'genres'
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('documentary', 'Documentary'),
        ('short', 'Short Film'),
    ]

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    description = models.TextField(blank=True, default='')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie')
    release_year = models.IntegerField(default=2024)
    duration = models.IntegerField(default=0, help_text='Duration in minutes')
    director = models.CharField(max_length=255, blank=True, default='')
    cast = models.TextField(blank=True, default='', help_text='Comma-separated cast names')
    rating = models.FloatField(default=0.0)
    maturity_rating = models.CharField(max_length=10, default='PG-13')

    # Media
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    poster_url = models.URLField(blank=True, default='')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, help_text='Smaller preview image for cards')
    thumbnail_url = models.URLField(blank=True, default='', help_text='External thumbnail URL')
    backdrop = models.ImageField(upload_to='backdrops/', blank=True, null=True)
    backdrop_url = models.URLField(blank=True, default='')
    trailer_url = models.URLField(blank=True, default='')
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)

    # Categorization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='movies')
    genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
    tags = models.TextField(blank=True, default='', help_text='Comma-separated tags')

    # Stats
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    trending_score = models.FloatField(default=0.0)

    # Status
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    requires_access = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    def get_poster_display(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or '/static/img/default-poster.jpg'

    def get_thumbnail_display(self):
        """Return thumbnail URL, fallback to poster if not set."""
        if self.thumbnail:
            return self.thumbnail.url
        if self.thumbnail_url:
            return self.thumbnail_url
        return self.get_poster_display()

    def get_backdrop_display(self):
        if self.backdrop:
            return self.backdrop.url
        return self.backdrop_url or self.get_poster_display()

    def get_genres_list(self):
        return list(self.genres.values_list('name', flat=True))

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def get_cast_list(self):
        return [c.strip() for c in self.cast.split(',') if c.strip()]


class Review(models.Model):
    """User review and rating for a movie."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=150, default='')
    user_avatar = models.URLField(blank=True, default='')
    rating = models.FloatField(help_text='User rating 1-10')
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='')
    contains_spoilers = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['movie', 'user_id']

    def __str__(self):
        return f"{self.username} - {self.movie.title} ({self.rating}/10)"


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    poster_url = models.URLField(blank=True, default='')
    movies = models.ManyToManyField(Movie, blank=True, related_name='playlists')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'playlists'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
