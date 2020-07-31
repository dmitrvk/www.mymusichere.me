# Licensed under the MIT License

from django.views.generic import ListView

from scores.models import Score


class IndexView(ListView):
    """Index page with all scores."""

    template_name = 'scores/index.html'
    queryset = Score.objects.all()  # pylint: disable=no-member

    def get(self, request):    # pylint: disable=arguments-differ
        self.request.session.set_test_cookie()
        return super().get(request)
