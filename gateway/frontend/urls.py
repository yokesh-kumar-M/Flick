from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('browse/', views.browse, name='browse'),
    path('movie/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('watch/<slug:slug>/', views.player, name='player'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_page, name='search'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('playlist/<slug:slug>/', views.playlist_page, name='playlist'),
    path('genre/<slug:slug>/', views.genre_page, name='genre'),
    path('payment/', views.payment_page, name='payment'),
    path('logout/', views.logout_view, name='logout'),
]
