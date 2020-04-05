from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic, View

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
    def get(self, request):
        return HttpResponse('Wrong request', status=400)

    def post(self, request):
        if self.is_request_valid(request):
            exitcode = os.system('%s' % settings.DEPLOY_SCORES_SCRIPT_PATH)
            if exitcode == 0:
                try:
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

                    return HttpResponse('Deployed successfully')
                except Exception as err:
                    return HttpResponse('Deploy failed', status=500)
            else:
                return HttpResponse('Deploy failed', status=500)
            return HttpResponse(response)
        else:
            return HttpResponse('Wrong request', status=400)


    def is_request_valid(self, request):
        if self.request_has_required_headers(request):
            if self.is_user_agent_valid(request):
                if self.is_signature_valid(request):
                    return True

        return False

    def request_has_required_headers(self, request):
        return \
            'X-Github-Event' in request.headers and \
            'X-Github-Delivery' in request.headers and \
            'X-Hub-Signature' in request.headers and \
            'User-Agent' in request.headers

    def is_user_agent_valid(self, request):
        user_agent = request.headers.get('User-Agent', 'None')
        return user_agent.startswith('GitHub-Hookshot/')

    def is_signature_valid(self, request):
        x_hub_signature = request.headers.get('X-Hub-Signature', 'None')
        hash_algorithm, github_signature = x_hub_signature.split('=')
        algorithm = hashlib.__dict__.get(hash_algorithm)
        encoded_secret = bytes(settings.WEBHOOK_SECRET, 'latin-1')
        mac = hmac.new(encoded_secret, msg=request.body, digestmod=algorithm)
        return hmac.compare_digest(mac.hexdigest(), github_signature)


