from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from .models import Score

def index(request):
    context = {
        'scores': Score.objects.all()
    }
    return render(request, 'scores/index.html', context)

def score_view(request, alias):
    score = get_object_or_404(Score, alias=alias)
    context = {
        'score': score
    }
    response = render(request, 'scores/score.html', context)
    return response

