from django.db import models


class Score(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(default='')
    slug = models.CharField(max_length=255, default='')
    path_to_file = models.CharField(max_length=255)
    github_link = models.CharField(max_length=255, default='https://github.com')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return '%s | %s' % (self.title, self.description)
