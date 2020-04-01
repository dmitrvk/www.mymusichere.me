from django.urls import path

from . import views

app_name = 'hooks'

urlpatterns = [
    path('deploy', views.deploy, name='deploy')
]
