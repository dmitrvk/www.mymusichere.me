from django.urls import path

from . import views

app_name = 'hooks'

urlpatterns = [
    path('build', views.build, name='build')
]
