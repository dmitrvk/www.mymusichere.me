# Licensed under the MIT License

import os

from django.conf import settings
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
    instruments = models.ManyToManyField('Instrument', blank=True)
    timestamp = models.DateTimeField(editable=False)
    views = models.PositiveIntegerField(default=0)

    @property
    def pdf_path(self) -> str:
        """Relative path to pdf file with score.

        Returned string should be appended to static URL.
        """
        if self.slug:
            return f'{self.slug}/{self.slug}.pdf'

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

            return False

        def get_path_from_dir_entry(dir_entry: os.DirEntry) -> str:
            """Return relative path to page or empty string if not a file."""
            if dir_entry.is_file():
                return f'{self.slug}/{dir_entry.name}'

            return ''

        def get_page_number_from_path(path: str) -> int:
            """Extract page number from page's path.

            For example, if path is 'scores/testscore/testscore-page12.png',
            the function returns 12.
            """
            return int(path.split('page')[1].split('.')[0])

        if self.slug:
            pages_dir = os.path.join(settings.MEDIA_ROOT, self.slug)

            if os.path.exists(pages_dir) and os.path.isdir(pages_dir):
                dir_entries = filter(dir_entry_is_page, os.scandir(pages_dir))
                paths = list(map(get_path_from_dir_entry, dir_entries))

                if len(paths) > 1:
                    paths.sort(key=get_page_number_from_path)

                return paths

            return []

        return []

    @property
    def thumbnail_path(self) -> str:
        """Relative path to thumbnail image."""
        if self.slug:
            return f'{self.slug}/{self.slug}-thumbnail.png'

        return ''

    @property
    def github_link(self) -> str:
        """Link to lilypond source files on GitHub."""
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                base = settings.GITHUB_SCORES_SOURCE_REPO
                return f'{base}/tree/master/{self.slug}'

            return settings.GITHUB_SCORES_SOURCE_REPO

        return 'https://github.com/'

    def save(self, *args, **kwargs):
        """Set timestamp when first created."""
        if not self.id:
            self.timestamp = timezone.now()

        return super(Score, self).save(*args, **kwargs)

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
        return f'{self.slug} ({self.title})'
