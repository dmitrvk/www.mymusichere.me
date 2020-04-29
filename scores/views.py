from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.decorators import method_decorator

from git import Repo
import subprocess

import os
import re
import hmac
import hashlib
import logging

from django.conf import settings
from .models import Score


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

        self.logger.info("Score '%s' accessed" % score.slug)

        return score



class PublishView(View):
    SPACE = r'\s*'
    LINE_BEGIN = r'^' + SPACE
    EQUALS_SIGN = SPACE + r'=' + SPACE
    VALUE = r'".*"'

    HEADER_START_PATTERN = r'\\header'
    TITLE_PATTERN = LINE_BEGIN + r'title' + EQUALS_SIGN + VALUE
    COMPOSER_PATTERN = LINE_BEGIN + r'composer' + EQUALS_SIGN + VALUE
    ARRANGER_PATTERN = LINE_BEGIN + r'arranger' + EQUALS_SIGN + VALUE
    INSTRUMENT_PATTERN = LINE_BEGIN + r'instruments*' + EQUALS_SIGN + VALUE

    logger = logging.getLogger(__name__)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PublishView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        if self.__is_request_valid(request):
            try:
                repo_dir = os.path.join(settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores')
                repo_scores = self.__get_repo_scores(repo_dir)

                db_scores = self.__get_db_scores()

                # Delete scores removed from repository
                scores_to_delete_slugs = db_scores.difference(repo_scores)
                Score.objects.filter(slug__in=scores_to_delete_slugs).delete()

                if scores_to_delete_slugs:
                    self.logger.info("Scores '%s' deleted" % "','".join(scores_to_delete_slugs))
                else:
                    self.logger.info('No scores deleted')


                # Create scores added to repository
                db_scores = self.__get_db_scores()
                new_scores_slugs = repo_scores.difference(db_scores)
                new_scores = [self.__create_score_from_header(slug) for slug in new_scores_slugs]
                Score.objects.bulk_create(new_scores)

                if new_scores_slugs:
                    self.logger.info("Scores '%s' created" % "','".join(new_scores_slugs))
                else:
                    self.logger.info('No scores created')


                # Update scores changed in repository
                db_scores = self.__get_db_scores()
                scores_to_update_slugs = db_scores.difference(new_scores_slugs)
                for slug in scores_to_update_slugs:
                    score_in_db = Score.objects.filter(slug=slug)[0]
                    score_in_repo = self.__create_score_from_header(slug)
                    if score_in_db != score_in_repo:
                        score_in_db.update_with_score(score_in_repo)
                    score_in_db.save()

                if scores_to_update_slugs:
                    self.logger.info("Scores '%s' updated" % "','".join(scores_to_update_slugs))
                else:
                    self.logger.info('No scores updated')

                return HttpResponse('DB updated successfully')
            except Exception as e:
                return HttpResponse('Failed to update DB. %s' % e, status=500)
        else:
            return HttpResponse('Wrong request', status=400)


    def __is_request_valid(self, request):
        if 'Authorization' in request.headers:
            header = request.headers.get('Authorization', 'None').split()
            return header[0] == 'Token' and header[1] == settings.PUBLISH_TOKEN
        else:
            return False

    def __get_repo_scores(self, repo_dir):
        return set([f.name for f in os.scandir(repo_dir) if f.is_dir()])

    def __get_db_scores(self):
        return set([score.slug for score in Score.objects.all()])

    def __create_score_from_header(self, score_slug):
        score = Score(title='', slug=score_slug)

        path_to_source = os.path.join(
            settings.MYMUSICHERE_REPO_DIR,
            score.slug,
            '%s.ly' % score.slug
        )

        reading_header = False
        for line in open(path_to_source):
            if not reading_header and re.search(self.HEADER_START_PATTERN, line):
                reading_header = True
            else:
                if '}' in line:
                    reading_header = False
                else:
                    match = re.search(self.TITLE_PATTERN, line)
                    if match and not score.title:
                        score.title = match.group().split('"')[1]
                        continue

                    match = re.search(self.COMPOSER_PATTERN, line)
                    if match and not score.composer:
                        score.composer = match.group().split('"')[1]
                        continue

                    match = re.search(self.ARRANGER_PATTERN, line)
                    if match and not score.arranger:
                        score.arranger = match.group().split('"')[1]
                        continue

                    match = re.search(self.INSTRUMENT_PATTERN, line)
                    if match and not score.instrument:
                        score.instrument = match.group().split('"')[1]
                        continue

        return score

