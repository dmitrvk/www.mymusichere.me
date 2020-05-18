import hashlib
import hmac
import logging
import os
import re
import subprocess
import urllib
from operator import methodcaller

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt

from .models import Arranger, Composer, Instrument, Score


class IndexView(generic.ListView):
    template_name = 'scores/index.html'
    queryset = Score.objects.all()

    def get(self, request):
        self.request.session.set_test_cookie()
        return super().get(request)


class ScoreView(generic.DetailView):
    model = Score
    template_name = 'scores/score.html'

    logger = logging.getLogger(__name__)

    def get_object(self):
        score = super().get_object()

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            if not self.request.session.get('viewed_score', False):
                score.views += 1
                score.save()
                self.request.session['viewed_score'] = True

        self.logger.info(f"Score '{score.slug}' accessed")

        return score


class PublishView(View):
    """Publish scores on the website.

    Publishing includes copying assets to static files dir and
    updating the database."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.repo_scores = set()
        with os.scandir(settings.MEDIA_ROOT) as dir_entries:
            for entry in dir_entries:
                if entry.is_dir():
                    self.repo_scores.add(entry.name)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PublishView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        self._delete_scores_removed_from_repo()
        self._update_changed_scores()
        self._create_scores_added_to_repo()
        return HttpResponse('Database updated.', content_type='text/plain')

    def post(self, request):
        if self._is_request_valid(request):
            try:
                self._delete_scores_removed_from_repo()
                self._update_changed_scores()
                self._create_scores_added_to_repo()
                return HttpResponse('DB updated successfully')
            except Exception as e:
                msg = f'Failed to update DB. {e}'
                return HttpResponseServerError(msg, content_type='text/plain')
        else:
            return HttpResponseBadRequest()

    def _is_request_valid(self, request) -> bool:
        if 'Authorization' in request.headers:
            header = request.headers.get('Authorization', 'None').split()
            return header[0] == 'Token' and header[1] == settings.PUBLISH_TOKEN
        else:
            return False

    def _get_db_scores(self) -> set:
        return set([score.slug for score in Score.objects.all()])

    def _get_score_header(self, slug: str) -> dict:
        """Download source of score with given slug and return its header."""
        header = dict()

        base_url = 'https://raw.githubusercontent.com'
        url = f'{base_url}/dmitrvk/mymusichere/master/{slug}/{slug}.ly'
        ly_file = urllib.request.urlopen(url)

        reading_header = False

        for line in ly_file:
            line = bytes.decode(line).strip()
            if reading_header:
                if '}' in line:
                    reading_header = False
                    break
                elif '=' in line:
                    field, value = map(methodcaller('strip'), line.split('='))
                    if len(field) > 0 and len(value) > 0:
                        if '"' in value:
                            value = value.strip('"')
                        if len(value) > 0:
                            header[field.lower()] = value
            elif '\header' in line:
                reading_header = True
        return header

    def _delete_scores_removed_from_repo(self) -> None:
        scores_to_delete = self._get_db_scores() - self.repo_scores
        if scores_to_delete:
            Score.objects.filter(slug__in=scores_to_delete).delete()
            self.logger.info(f'Scores {scores_to_delete} deleted.')

    def _update_changed_scores(self) -> None:
        for slug in self._get_db_scores():
            header = self._get_score_header(slug)
            score = Score.objects.filter(slug=slug)[0]
            score.update_with_header(header)
            self.logger.info(f"Score '{slug}' updated.")

    def _create_scores_added_to_repo(self) -> None:
        for slug in (self.repo_scores - self._get_db_scores()):
            header = self._get_score_header(slug)
            score = Score(slug=slug)
            score.update_with_header(header)
            self.logger.info(f"Score '{slug}' created.")

