from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic, View

from git import Repo
import subprocess

import os
import hmac
import hashlib

from mymusichere import settings
from .models import Score


class IndexView(generic.ListView):
    template_name = 'scores/index.html'

    def get_queryset(self):
        return Score.objects.all()


class ScoreView(generic.DetailView):
    model = Score
    template_name = 'scores/score.html'


class DeployView(View):
    def post(self, request):
        if self.is_token_valid(request):
            Score.objects.all().delete()

            scores_dir = os.path.join(settings.STATIC_ROOT, 'scores')

            for f in os.scandir(scores_dir):
                if f.is_dir():
                    s = Score(title='', slug=f.name)
                    path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, s.slug, '%s.ly' % s.slug)
                    for line in open(path_to_source):
                        if 'title' in line:
                            s.title = line.split('"')[1]
                            break

                    s.save()

            return HttpResponse('DB updated successfully')
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

