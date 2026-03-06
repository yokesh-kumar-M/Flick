from django.contrib import admin
from .models import MovieFeature, UserInteraction, CachedRecommendation

@admin.register(MovieFeature)
class MovieFeatureAdmin(admin.ModelAdmin):
    list_display = ['movie_id', 'title', 'year', 'rating', 'view_count', 'trending_score']

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie_id', 'interaction_type', 'score', 'created_at']

@admin.register(CachedRecommendation)
class CachedRecommendationAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'recommendation_type', 'updated_at']
