# backend/sapbot_api/urls.py
from django.urls import path, include
from django.contrib import admin
from ..admin.document_admin import admin_site

# Admin URL'leri için custom pattern
admin_patterns = [
    path('admin/', admin.site.urls),
    path('sapbot-admin/', admin_site.urls),  # Custom admin site
]

# Ana URL patterns
urlpatterns = [
    # API endpoints
    path('api/v1/', include('sapbot_api.api.urls')),
    
    # Admin interfaces
    path('', include(admin_patterns)),
    
    # Health check
    path('health/', include('sapbot_api.health.urls')),
]