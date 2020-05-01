from django.urls import path

from . import views


app_name = 'scores'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('scores/publish', views.PublishView.as_view(), name='publish'),
    path('<slug:slug>', views.ScoreView.as_view(), name='score')
]
