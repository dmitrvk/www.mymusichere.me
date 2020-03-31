import os

from django.db import models

from mymusichere import settings

class Score(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    is_finished = models.BooleanField(default=True)

    def get_path_to_pdf(self):
        if self.slug:
            return 'scores/%s/%s.pdf' % (self.slug, self.slug)
        else:
            return ''

    def get_paths_to_pages(self):
        if self.slug:
            if settings.DEBUG:
                pages_dir = os.path.join(settings.BASE_DIR, 'scores', 'static', 'scores', self.slug)
            else:
                pages_dir = os.path.join(settings.STATIC_ROOT, 'scores', '%s' % self.slug)

            return [os.path.join('scores', self.slug, page.name)
                    for page in os.scandir(pages_dir)
                    if page.name.startswith('%s-page' % self.slug)]
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
