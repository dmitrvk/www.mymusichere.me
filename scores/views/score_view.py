from django.views.generic import DetailView

from scores.models import Score


class ScoreView(DetailView):  # pylint: disable=too-few-public-methods
    """Page with sheet music for a score."""

    model = Score
    template_name = 'scores/score.html'

    def get_object(self):
        score = super().get_object()

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            if not self.request.session.get('viewed_score', False):
                score.views += 1
                score.save()
                self.request.session['viewed_score'] = True

        return score
