import datetime
import os

from django.conf import settings
from django.db import models
from django.utils import timezone


class Score(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, default='')
    arranger = models.CharField(max_length=255, default='')
    instruments = models.CharField(max_length=255, default='')
    last_modified = models.DateTimeField(default=datetime.datetime(2020, 1, 1))
    views = models.IntegerField(default=0)


    def get_path_to_pdf(self) -> str:
        if self.slug:
            return f'scores/{self.slug}/{self.slug}.pdf'
        else:
            return ''

    def get_paths_to_pages(self) -> list:
        if self.slug:
            pages_dir = os.path.join(settings.STATIC_ROOT, 'scores', self.slug)

            if os.path.exists(pages_dir) and os.path.isdir(pages_dir):
                paths_to_pages = [os.path.join('scores', self.slug, page.name)
                        for page in os.scandir(pages_dir)
                        if page.name.startswith(f'{self.slug}-page')
                        or page.name == f'{self.slug}.png']

                if len(paths_to_pages) > 1:
                    paths_to_pages.sort(key=lambda path : path.split('page')[1].split('.')[0])

                return paths_to_pages
            else:
                return []
        else:
            return []

    def get_thumbnail_path(self) -> str:
        if self.slug:
            return f'scores/{self.slug}/thumbnail.png'
        else:
            return ''

    def get_link_to_source(self) -> str:
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                return settings.GITHUB_SCORES_SOURCE_REPO + f'/tree/master/{self.slug}/'
            else:
                return settings.GITHUB_SCORES_SOURCE_REPO
        else:
            return 'https://github.com/'

    class Meta:
        ordering = ['title']

    def update_with_score(self, score) -> None:
        self.title = score.title
        self.composer = score.composer
        self.arranger = score.arranger
        self.instruments = score.instruments
        self.last_modified = timezone.now()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
            self.slug == other.slug and \
            self.title == other.title and \
            self.composer == other.composer and \
            self.arranger == other.arranger and \
            self.instruments == other.instruments

    def __str__(self):
        return f'{self.slug} ({self.title}, {self.composer}, {self.arranger}, {self.instruments})'

    def __hash__(self):
        return hash((self.id, self.title))
