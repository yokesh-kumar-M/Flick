from django.urls import path, re_path
from .proxy import proxy_view

urlpatterns = [
    re_path(r'^(?P<service>auth|catalog|access|streaming|recommendations|notifications)/(?P<path>.*)$',
            proxy_view, name='proxy'),
]
