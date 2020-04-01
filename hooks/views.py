from django.shortcuts import render
from django.http import HttpResponse, Http404

import os

from mymusichere import settings
from scores.models import Score

def deploy(request):
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

                    for line in open(path_to_source):
                        if 'status' in line:
                            status = line.split('"')[1]
                            if status == "unfinished":
                                s.is_finished = False
                            break

                    s.save()

            response = '{ "code": 200, "message": "OK" }'
        except Exception as err:
            response = '{ "code": 500, "message": "Failed to update database.  Error: %s" }' % err
    else:
        response = '{ "code": 500, "message": "Failed to execute deploy script" }'
    return HttpResponse(response)
