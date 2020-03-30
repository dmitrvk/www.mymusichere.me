from django.shortcuts import render
from django.http import HttpResponse, Http404

import os

from mymusichere import settings
from scores.models import Score

def build(request):
    exitcode = os.system('%s' % settings.SCORES_BUILD_SCRIPT_PATH)
    if exitcode == 0:
        try:
            Score.objects.all().delete()

            if settings.DEBUG:
                scores_dir = os.path.join(settings.BASE_DIR, 'scores', 'static', 'scores')
            else:
                scores_dir = os.path.join(settings.STATIC_ROOT, 'scores')

            for f in os.scandir(scores_dir):
                if f.is_dir():
                    s = Score(title='', slug=f.name)
                    path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, s.slug, '%s.ly' % s.slug)
                    for line in open(path_to_source):
                        if 'title' in line:
                            s.title = line.split('"')[1]

                    s.save()

            response = '{ code: 200 }'
        except:
            response = '{ code: 500 }'
    else:
        response = '{ code: 500 }'
    return HttpResponse(response)
