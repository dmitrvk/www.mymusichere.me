"""
mymusichere URL Configuration
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', include('scores.urls'))
]


# Serve static files during development

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
