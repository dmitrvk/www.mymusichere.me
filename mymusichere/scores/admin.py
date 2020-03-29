from django.contrib import admin

from .models import Score

admin.site.register(Score)
admin.site.site_header = 'MyMusicHere Administration'
