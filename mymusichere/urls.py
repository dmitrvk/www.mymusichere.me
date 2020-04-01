"""
mymusichere URL Configuration
"""

from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hooks/', include('hooks.urls')),
    path('', include('scores.urls'))
]


# Serve static files during development

from django.conf import settings

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

