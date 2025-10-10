"""
URL configuration for safe_eats_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve
import os

def health_check(request):
    """Simple health check endpoint for AWS Elastic Beanstalk"""
    return JsonResponse({"status": "healthy"})

def serve_react(request, path=''):
    """Serve React frontend"""
    if path and os.path.exists(os.path.join(settings.STATIC_ROOT, path)):
        return serve(request, path, document_root=settings.STATIC_ROOT)
    return serve(request, 'index.html', document_root=settings.STATIC_ROOT)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/restaurants/", include("inspections.urls")),
    path("health/", health_check, name="health_check"),
    # Serve React app for all other routes
    re_path(r'^(?P<path>.*)$', serve_react, name='serve_react'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)