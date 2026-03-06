from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/password/', views.change_password, name='change_password'),
    path('profile/avatar/', views.upload_avatar, name='upload_avatar'),
    path('history/', views.watch_history, name='watch_history'),
    path('history/update/', views.update_watch_progress, name='update_watch_progress'),
    path('continue-watching/', views.continue_watching, name='continue_watching'),
    path('genre-stats/', views.genre_stats, name='genre_stats'),
    path('stats/', views.user_stats, name='user_stats'),
    path('validate/', views.validate_token, name='validate_token'),
    path('users/', views.list_users, name='list_users'),
    # Admin endpoints
    path('users/<int:user_id>/toggle-admin/', views.toggle_admin, name='toggle_admin'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('users/<int:user_id>/toggle-super-access/', views.toggle_super_access, name='toggle_super_access'),
    path('admin-stats/', views.admin_stats, name='admin_stats'),
    # Watchlist
    path('watchlist/', views.get_watchlist, name='get_watchlist'),
    path('watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('watchlist/check/<int:movie_id>/', views.check_watchlist, name='check_watchlist'),
]
