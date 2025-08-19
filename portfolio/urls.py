"""
URL configuration for portfolio project.

Main URL routing configuration that includes all app URLs
and handles media files in development mode.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

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

# Serve media files during development
# In production, your web server (nginx/apache) should handle this
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Optional: Also serve static files in development if needed
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)