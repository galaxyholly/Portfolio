"""
URL configuration for portfolio project.

Main URL routing configuration that includes all app URLs
and handles media files in development mode.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path


urlpatterns = [
    # Blog application URLs
    path("blog/", include("blog.urls")),
    
    # User registration and authentication
    path('registration/', include('registration.urls')),
    
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Built-in Django auth views (login, logout, password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Main/home page URLs - keep this last as it likely has a catch-all
    path('', include('main.urls')),
]

# Serve media files in production
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve static and media files
if settings.DEBUG:
    # In development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production - static files handled by WhiteNoise
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Media files need to be served manually in production
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
