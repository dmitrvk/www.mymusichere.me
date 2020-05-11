import datetime
import os

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Score(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255)
    composer = models.ForeignKey(
            'Composer',
            on_delete=models.SET_NULL,
            blank=True,
            null=True
    )
    arranger = models.ForeignKey(
            'Arranger',
            on_delete=models.SET_NULL,
            blank=True,
            null=True
    )
    instruments = models.ManyToManyField('Instrument')
    last_modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    @property
    def pdf_path(self) -> str:
        """Relative path to pdf file with score.

        Returned string should be appended to static URL.
        """
        if self.slug:
            return f'scores/{self.slug}/{self.slug}.pdf'
        else:
            return ''

    @property
    def pages_paths(self) -> list:
        """List of relative paths to pages.

        Each item in the list is a string like
        'scores/testscore/testscore.png' (if only one page present) or
        'scores/testscore/testscore-page1.png',
        where 'testscore' is score's slug and '1' is page number.
        Returned strings should be appended to the static URL.
        If slug is empty, an empty list is returned.
        """
        def dir_entry_is_page(dir_entry: os.DirEntry) -> bool:
            """Return true if dir entry is score's page."""
            if dir_entry.is_file():
                return (dir_entry.name == f'{self.slug}.png' or
                        dir_entry.name.startswith(f'{self.slug}-page'))
            else:
                return False

        def get_path_from_dir_entry(dir_entry: os.DirEntry) -> str:
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
                dir_entries = filter(dir_entry_is_page, os.scandir(pages_dir))
                paths = list(map(get_path_from_dir_entry, dir_entries))

                if len(paths) > 1:
                    paths.sort(key=get_page_number_from_path)

                return paths
            else:
                return []
        else:
            return []

    @property
    def thumbnail_path(self) -> str:
        if self.slug:
            return f'scores/{self.slug}/thumbnail.png'
        else:
            return ''

    @property
    def github_link(self) -> str:
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                base = settings.GITHUB_SCORES_SOURCE_REPO
                return f'{base}/tree/master/{self.slug}'
            else:
                return settings.GITHUB_SCORES_SOURCE_REPO
        else:
            return 'https://github.com/'

    class Meta:
        ordering = ['title']

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.slug == other.slug and
                self.title == other.title and
                self.composer == other.composer and
                self.arranger == other.arranger and
                list(self.instruments.all()) == list(other.instruments.all()))

    def __hash__(self):
        return hash((self.id, self.title))

    def __str__(self):
        return (f'{self.slug} ({self.title})')


class Composer(models.Model):
    """Represents a composer of a score."""

    name = models.CharField(max_length=255, unique=True)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.name == other.name)

    def __hash__(self):
        return hash((self.id, self.name))

    def __str__(self):
        return self.name


class Arranger(models.Model):
    """Represents an arranger of a score."""

    name = models.CharField(max_length=255, unique=True)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.name == other.name)

    def __hash__(self):
        return hash((self.id, self.name))

    def __str__(self):
        return self.name


class Instrument(models.Model):
    """Represents an instrument on which the score is played."""

    name = models.CharField(max_length=255, unique=True)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self.name == other.name)

    def __hash__(self):
        return hash((self.id, self.name))

    def __str__(self):
        return self.name
