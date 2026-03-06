from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('homepage/', views.homepage_data, name='homepage_data'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Genres
    path('genres/', views.genre_list, name='genre_list'),
    path('genres/create/', views.genre_create, name='genre_create'),
    path('genres/<slug:slug>/', views.genre_movies, name='genre_movies'),
    path('genres/<int:pk>/update/', views.genre_update, name='genre_update'),
    path('genres/<int:pk>/delete/', views.genre_delete, name='genre_delete'),

    # Movies
    path('movies/', views.movie_list, name='movie_list'),
    path('movies/create/', views.movie_create, name='movie_create'),
    path('movies/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:pk>/update/', views.movie_update, name='movie_update'),
    path('movies/<int:pk>/delete/', views.movie_delete, name='movie_delete'),
    path('movies/<int:pk>/like/', views.increment_like, name='increment_like'),

    # Reviews
    path('movies/<int:pk>/reviews/', views.movie_reviews, name='movie_reviews'),
    path('reviews/create/', views.create_review, name='create_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('reviews/<int:pk>/like/', views.like_review, name='like_review'),
    path('reviews/mine/', views.user_reviews, name='user_reviews'),

    # Search
    path('search/', views.search, name='search'),

    # Collections
    path('trending/', views.trending, name='trending'),
    path('featured/', views.featured, name='featured'),
    path('new-releases/', views.new_releases, name='new_releases'),

    # Playlists
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/create/', views.playlist_create, name='playlist_create'),
    path('playlists/<slug:slug>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/<int:pk>/update/', views.playlist_update, name='playlist_update'),
    path('playlists/<int:pk>/delete/', views.playlist_delete, name='playlist_delete'),

    # Admin Stats
    path('admin-stats/', views.admin_stats, name='admin_stats'),
]
