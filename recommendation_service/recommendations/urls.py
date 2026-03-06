from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_recommendations, name='get_recommendations'),
    path('similar/<int:movie_id>/', views.get_similar, name='get_similar'),
    path('trending/', views.get_trending, name='get_trending'),
    path('interaction/', views.record_interaction, name='record_interaction'),
    path('sync-movies/', views.sync_movies, name='sync_movies'),
    path('recalculate/', views.trigger_recalculation, name='trigger_recalculation'),
]
