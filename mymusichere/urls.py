# Licensed under the MIT License

"""mymusichere URL Configuration."""

from django import urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    urls.path('admin/doc/', urls.include('django.contrib.admindocs.urls')),
    urls.path('admin/', admin.site.urls),
    urls.path('', urls.include('scores.urls'))
]


# Serve static files during development

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [
        urls.path('__debug__/', urls.include(debug_toolbar.urls)),
    ] + urlpatterns
