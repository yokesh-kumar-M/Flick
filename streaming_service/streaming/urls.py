from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_stream, name='start_stream'),
    path('heartbeat/', views.heartbeat, name='heartbeat'),
    path('end/', views.end_stream, name='end_stream'),
    path('transcode/', views.transcode, name='transcode'),
    path('transcode/<int:job_id>/', views.transcode_status, name='transcode_status'),
    path('active-streams/', views.active_streams, name='active_streams'),
    path('hls/<int:movie_id>/<str:filename>', views.serve_hls, name='serve_hls'),
    path('hls/<int:movie_id>/<str:quality>/<str:filename>', views.serve_hls_quality, name='serve_hls_quality'),
]
