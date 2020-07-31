# Licensed under the MIT License

from django.urls import path

from scores import views

app_name = 'scores'  # pylint: disable=invalid-name

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('scores/publish', views.PublishView.as_view(), name='publish'),
    path('<slug:slug>', views.ScoreView.as_view(), name='score')
]
