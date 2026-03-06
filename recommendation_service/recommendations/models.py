from django.db import models
import json


class MovieFeature(models.Model):
    """Cached movie features for recommendation calculations."""
    movie_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=500)
    genres = models.TextField(default='[]')  # JSON list
    tags = models.TextField(default='[]')   # JSON list
    director = models.CharField(max_length=255, blank=True, default='')
    year = models.IntegerField(default=2024)
    rating = models.FloatField(default=0.0)
    view_count = models.IntegerField(default=0)
    trending_score = models.FloatField(default=0.0)
    feature_vector = models.TextField(default='')  # Serialized feature text for TF-IDF
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movie_features'

    def get_genres(self):
        return json.loads(self.genres) if self.genres else []

    def get_tags(self):
        return json.loads(self.tags) if self.tags else []

    def __str__(self):
        return f"{self.title} (ID: {self.movie_id})"


class UserInteraction(models.Model):
    """User-movie interaction for collaborative filtering."""
    user_id = models.IntegerField(db_index=True)
    movie_id = models.IntegerField(db_index=True)
    interaction_type = models.CharField(max_length=20)  # view, like, complete, rate
    score = models.FloatField(default=1.0)  # Interaction weight
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_interactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"User {self.user_id} → Movie {self.movie_id} ({self.interaction_type})"


class CachedRecommendation(models.Model):
    """Pre-computed recommendations cached per user."""
    RECOMMENDATION_TYPES = [
        ('personalized', 'Personalized'),
        ('similar', 'Similar'),
        ('collaborative', 'Collaborative'),
        ('trending', 'Trending'),
    ]

    user_id = models.IntegerField(db_index=True)
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    movie_ids = models.TextField(default='[]')  # JSON list of movie IDs
    scores = models.TextField(default='[]')     # JSON list of scores
    source_movie_id = models.IntegerField(null=True, blank=True)  # For "similar" type
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cached_recommendations'

    def get_movie_ids(self):
        return json.loads(self.movie_ids) if self.movie_ids else []

    def get_scores(self):
        return json.loads(self.scores) if self.scores else []

    def __str__(self):
        return f"User {self.user_id} - {self.recommendation_type}"
