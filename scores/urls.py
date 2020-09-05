# Licensed under the MIT License

from django import urls
from scores import views

app_name = 'scores'  # pylint: disable=invalid-name

urlpatterns = [
    urls.path('', views.IndexView.as_view(), name='index'),
    urls.path('scores/publish', views.PublishView.as_view(), name='publish'),
    urls.path('<slug:slug>', views.ScoreView.as_view(), name='score')
]
