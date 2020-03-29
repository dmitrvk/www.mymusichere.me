from django.db import models

from mymusichere import settings

class Score(models.Model):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

    def get_filename(self):
        if self.slug:
            return '%s/%s.pdf' % (self.slug, self.slug)
        else:
            return ''

    def get_link_to_source(self):
        if settings.GITHUB_SCORES_SOURCE_REPO:
            if self.slug:
                return settings.GITHUB_SCORES_SOURCE_REPO \
                        + 'tree/master/%s/' % self.slug
            else:
                return settings.GITHUB_SCORES_SOURCE_REPO
        else:
            return 'https://github.com/'

    class Meta:
        ordering = ['title']

    def __str__(self):
        return '%s | %s' % (self.title, self.description)
