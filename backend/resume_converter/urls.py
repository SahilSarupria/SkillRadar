from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/resumes/', include('resumes.urls')),
    path('api/analyzer/', include('analyzer.urls')),
    path('api/skills/', include('skills.urls')),
    path('api/recommendations/', include('recommendations.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
