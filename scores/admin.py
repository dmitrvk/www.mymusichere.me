# Licensed under the MIT License

from django.contrib import admin

from scores import models

admin.site.register(models.Arranger)
admin.site.register(models.Composer)
admin.site.register(models.Instrument)
admin.site.register(models.Score)
admin.site.site_header = 'MyMusicHere Administration'
