from django.urls import path, re_path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:alias>', views.score_view, name='score_view')
]
