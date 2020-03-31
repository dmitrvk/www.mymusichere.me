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
