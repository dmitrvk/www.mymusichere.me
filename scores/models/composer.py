# Licensed under the MIT License

from django.db import models


class Composer(models.Model):
    """Represents a composer of a score."""

    name = models.CharField(max_length=255, unique=True)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash((self.id, self.name))

    def __str__(self):
        return self.name
