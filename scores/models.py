import datetime
import os

from django.conf import settings
from django.db import models
from django.utils import timezone


class Score(models.Model):
    slug = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, default='')
    arranger = models.CharField(max_length=255, default='')
    instruments = models.CharField(max_length=255, default='')
    last_modified = models.DateTimeField(default=datetime.datetime(2020, 1, 1))
    views = models.IntegerField(default=0)


    def get_pdf_path(self) -> str:
        """Relative path to pdf file with score.

        Returned string should be appended to static URL.
        """
        if self.slug:
            return f'scores/{self.slug}/{self.slug}.pdf'
        else:
            return ''

    def get_pages_paths(self) -> list:
        """List of relative paths to pages.

        Returned strings should be appended to static URL.
        """
        if self.slug:
            pages_dir = os.path.join(settings.STATIC_ROOT, 'scores', self.slug)

            if os.path.exists(pages_dir) and os.path.isdir(pages_dir):
                pages_paths = []
                for page in os.scandir(pages_dir):
                    if self._file_is_score_page(page.name):
                        page_path = f'scores/{self.slug}/{page.name}'
                        pages_paths.append(page_path)

                if len(pages_paths) > 1:
                    pages_paths.sort(
                        key=lambda name: self._get_page_number_from_filename(name)
                    )

                return pages_paths
            else:
                return []
        else:
            return []

    def _file_is_score_page(self, filename: str) -> bool:
        return (filename.startswith(f'{self.slug}-page') or
                filename == f'{self.slug}.png')

    def _get_page_number_from_filename(self, filename: str) -> str:
        return int(filename.split('page')[1].split('.')[0])

    def get_thumbnail_path(self) -> str:
        if self.slug:
            return f'scores/{self.slug}/thumbnail.png'
        else:
            return ''

    def get_link_to_source(self) -> str:
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                base = settings.GITHUB_SCORES_SOURCE_REPO
                return f'{base}/tree/master/{self.slug}'
            else:
                return settings.GITHUB_SCORES_SOURCE_REPO
        else:
            return 'https://github.com/'

    def update_with_score(self, score) -> None:
        self.title = score.title
        self.composer = score.composer
        self.arranger = score.arranger
        self.instruments = score.instruments
        self.last_modified = timezone.now()

    class Meta:
        ordering = ['title']

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.slug == other.slug and
                self.title == other.title and
                self.composer == other.composer and
                self.arranger == other.arranger and
                self.instruments == other.instruments)

    def __str__(self):
        return f'{self.slug} ({self.title}, {self.composer}, {self.arranger}, {self.instruments})'

    def __hash__(self):
        return hash((self.id, self.title))

