# Licensed under the MIT License

from django.views import generic
from scores import models


class IndexView(generic.ListView):
    """Index page with all scores."""

    template_name = 'scores/index.html'
    queryset = models.Score.objects.all()  # pylint: disable=no-member

    def get(self, request):    # pylint: disable=arguments-differ
        self.request.session.set_test_cookie()
        return super().get(request)
