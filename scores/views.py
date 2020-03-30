from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Score


class IndexView(generic.ListView):
    template_name = 'scores/index.html'

    def get_queryset(self):
        return Score.objects.all()


class ScoreView(generic.DetailView):
    model = Score
    template_name = 'scores/score.html'
