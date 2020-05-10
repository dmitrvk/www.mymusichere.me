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

        Each item in the list is a string like
        'scores/testscore/testscore.png' (if only one page present) or
        'scores/testscore/testscore-page1.png',
        where 'testscore' is score's slug and '1' is page number.
        Returned strings should be appended to the static URL.
        If slug is empty, an empty list is returned.
        """
        def dir_entry_is_score_page(dir_entry: os.DirEntry) -> bool:
            """Return true if dir entry is score's page."""
            if dir_entry.is_file():
                return (dir_entry.name == f'{self.slug}.png' or
                        dir_entry.name.startswith(f'{self.slug}-page'))
            else:
                return False

        def get_relative_path_from_dir_entry(dir_entry: os.DirEntry) -> str:
            """Return relative path to page or empty string if not a file."""
            if dir_entry.is_file():
                return f'scores/{self.slug}/{dir_entry.name}'
            else:
                return ''

        def get_page_number_from_path(path: str) -> int:
            """Extract page number from page's path.

            For example, if path is 'scores/testscore/testscore-page12.png',
            the function returns 12.
            """
            print(f'PATH {path}')
            return int(path.split('page')[1].split('.')[0])

        if self.slug:
            pages_dir = os.path.join(settings.STATIC_ROOT, 'scores', self.slug)

            if os.path.exists(pages_dir) and os.path.isdir(pages_dir):
                dir_entries = filter(dir_entry_is_score_page, os.scandir(pages_dir))
                paths = list(map(get_relative_path_from_dir_entry, dir_entries))

                if len(paths) > 1:
                    paths.sort(key=get_page_number_from_path)

                return paths
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
        return (f'{self.slug} ({self.title}, {self.composer}, '
                f'{self.arranger}, {self.instruments})')

    def __hash__(self):
        return hash((self.id, self.title))

