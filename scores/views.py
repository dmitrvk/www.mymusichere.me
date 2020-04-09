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

from mymusichere import settings
from .models import Score


class IndexView(generic.ListView):
    template_name = 'scores/index.html'
    queryset = Score.objects.all()


class ScoreView(generic.DetailView):
    model = Score
    template_name = 'scores/score.html'

    def get_object(self):
        score = super().get_object()
        score.views += 1
        score.save()
        return score


class DeployView(View):
    SPACE = r'\s*'
    LINE_BEGIN = r'^' + SPACE
    EQUALS_SIGN = SPACE + r'=' + SPACE
    VALUE = r'".*"'

    HEADER_START_PATTERN = r'\\header'
    TITLE_PATTERN = LINE_BEGIN + r'title' + EQUALS_SIGN + VALUE
    COMPOSER_PATTERN = LINE_BEGIN + r'composer' + EQUALS_SIGN + VALUE
    ARRANGER_PATTERN = LINE_BEGIN + r'arranger' + EQUALS_SIGN + VALUE
    INSTRUMENT_PATTERN = LINE_BEGIN + r'instrument' + EQUALS_SIGN + VALUE


    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeployView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        if self.is_request_valid(request):
            try:
                scores_repo_dir = os.path.join(settings.STATIC_ROOT, 'scores')
                scores_in_repo_slugs = set([f.name for f in os.scandir(scores_repo_dir) if f.is_dir()])

                # Delete scores removed from repository
                scores_in_db_slugs = set([s.slug for s in Score.objects.all()])
                scores_to_delete_slugs = scores_in_db_slugs.difference(scores_in_repo_slugs)
                Score.objects.filter(slug__in=scores_to_delete_slugs).delete()


                # Create scores added to repository
                scores_in_db_slugs = set([s.slug for s in Score.objects.all()])
                new_scores_slugs = scores_in_repo_slugs.difference(scores_in_db_slugs)
                new_scores = [self.create_score_from_header(slug) for slug in new_scores_slugs]
                Score.objects.bulk_create(new_scores)


                # Update scores changed in repository
                scores_in_db_slugs = set([s.slug for s in Score.objects.all()])
                scores_to_update_slugs = scores_in_db_slugs.difference(new_scores_slugs)
                for slug in scores_to_update_slugs:
                    score_in_db = Score.objects.filter(slug=slug)[0]
                    score_in_repo = self.create_score_from_header(slug)
                    if score_in_db != score_in_repo:
                        score_in_db.update_with_score(score_in_repo)
                    score_in_db.save()

                return HttpResponse('DB updated successfully')
            except Exception as e:
                return HttpResponse('Failed to update DB. %s' % e, status=500)
        else:
            return HttpResponse('Wrong request', status=400)


    def is_request_valid(self, request):
        return 'Authorization' in request.headers and self.is_token_valid(request)

    def is_token_valid(self, request):
        auth_header = request.headers.get('Authorization', 'None')
        auth_header_parts = auth_header.split()
        return \
            auth_header_parts[0] == 'Token' and \
            auth_header_parts[1] == settings.DEPLOY_TOKEN

    def create_score_from_header(self, score_slug):
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

