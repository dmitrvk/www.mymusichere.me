from django.contrib import admin

from .models import Arranger, Composer, Instrument, Score

admin.site.register(Arranger)
admin.site.register(Composer)
admin.site.register(Instrument)
admin.site.register(Score)
admin.site.site_header = 'MyMusicHere Administration'
