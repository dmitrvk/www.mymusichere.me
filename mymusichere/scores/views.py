from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import Score

def index(request):
    scores_count = len(Score.objects.all())
    context = {
        'scores_count': scores_count
    }
    return render(request, 'scores/index.html', context)

def score_view(request, title):
    score = get_object_or_404(Score, title=title)
    context = {
        'score_title': score.title,
        'score_path_to_file': score.path_to_file
    }
    response = render(request, 'scores/score.html', context)
    return response

