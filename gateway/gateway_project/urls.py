from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from frontend.health_views import health_check, metrics


def health_check_old(request):
    return JsonResponse({'status': 'ok', 'service': 'gateway'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('metrics/', metrics),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('proxy/', include('frontend.proxy_urls')),
    path('', include('frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
