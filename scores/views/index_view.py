from django.views.generic import ListView

from scores.models import Score


class IndexView(ListView):
    """Index page with all scores."""

    template_name = 'scores/index.html'
    queryset = Score.objects.all()

    def get(self, request):
        self.request.session.set_test_cookie()
        return super().get(request)
