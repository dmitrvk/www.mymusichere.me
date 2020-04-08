import datetime
import os

from django.db import models

from mymusichere import settings

class Score(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    composer = models.CharField(max_length=255, default='')
    arranger = models.CharField(max_length=255, default='')
    instrument = models.CharField(max_length=255, default='')
    last_modified = models.DateTimeField(default=datetime.datetime(2020, 1, 1))
    views = models.IntegerField(default=0)


    def get_path_to_pdf(self):
        if self.slug:
            return 'scores/%s/%s.pdf' % (self.slug, self.slug)
        else:
            return ''

    def get_paths_to_pages(self):
        if self.slug:
            pages_dir = os.path.join(settings.STATIC_ROOT, 'scores', '%s' % self.slug)

            paths_to_pages = [os.path.join('scores', self.slug, page.name)
                    for page in os.scandir(pages_dir)
                    if page.name.startswith('%s-page' % self.slug)
                    or page.name == '%s.png' % self.slug]

            if len(paths_to_pages) > 1:
                paths_to_pages.sort(key=lambda path : path.split('page')[1].split('.')[0])

            return paths_to_pages
        else:
            return ''

    def get_link_to_source(self):
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                return settings.GITHUB_SCORES_SOURCE_REPO \
                        + '/tree/master/%s/' % self.slug
            else:
                return settings.GITHUB_SCORES_SOURCE_REPO
        else:
            return 'https://github.com/'

    class Meta:
        ordering = ['title']

    def __str__(self):
        return '%s (%s)' % (self.slug, self.title)
