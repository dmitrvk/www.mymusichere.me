from django.urls import path, re_path

from . import views

app_name = 'scores'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<slug:slug>', views.ScoreView.as_view(), name='score')
]
