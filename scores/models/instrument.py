# Licensed under the MIT License

from django.db import models


class Instrument(models.Model):
    """Represents an instrument on which the score is played."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash((self.id, self.name))

    def __str__(self):
        return self.name
