from django.contrib import admin
from .models import Category, Genre, Movie, Playlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'release_year', 'rating', 'view_count', 'is_featured', 'is_active']
    list_filter = ['content_type', 'is_featured', 'is_active', 'genres', 'category']
    search_fields = ['title', 'director', 'cast', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['genres']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured', 'order']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['movies']
