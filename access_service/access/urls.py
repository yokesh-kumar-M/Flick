from django.urls import path
from . import views

urlpatterns = [
    # Access requests
    path('request/', views.request_access, name='request_access'),
    path('check/<int:movie_id>/', views.check_access, name='check_access'),
    path('verify/', views.verify_code, name='verify_code'),
    
    
    # Hash/Unlock endpoints
    path('unlock/', views.unlock_movie, name='unlock_movie'),
    path('generate_hash/', views.generate_hash_manual, name='generate_hash_manual'),

    # User endpoints
    path('my-requests/', views.my_requests, name='my_requests'),
    path('my-grants/', views.my_grants, name='my_grants'),
    
    # Admin endpoints
    path('approve/<int:pk>/', views.approve_access, name='approve_access'),
    path('deny/<int:pk>/', views.deny_access, name='deny_access'),
    path('pending/', views.pending_requests, name='pending_requests'),
    path('all/', views.all_requests, name='all_requests'),
    
    # Payment processing
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    path('payment/confirm/<int:request_id>/', views.confirm_payment_manual, name='confirm_payment_manual'),
    path('resend/<int:request_id>/', views.resend_access_code, name='resend_access_code'),
]
