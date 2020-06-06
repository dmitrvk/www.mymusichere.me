import os
import unittest
from unittest.mock import MagicMock

from django.conf import settings
from django.http import HttpRequest
from django.test import Client, TestCase
from django.urls import reverse
from pyfakefs.fake_filesystem_unittest import patchfs

from scores.models import Arranger, Composer, Instrument, Score
from scores.views import PublishView


class PublishViewTest(TestCase):
    def setUp(self):
        self.auth_token = 'Token {}'.format(settings.PUBLISH_TOKEN)

        self.client = Client(HTTP_AUTHORIZATION=self.auth_token)
        self.client_no_auth = Client()

        self.test_slugs = {'testscore1', 'testscore2', 'testscore3'}

        self.test_lilypond_header = """
        \header {
            title = "Test Score"
            subtitle = "Subtitle"
            composer = "Composed by Composer"
            arranger = "Arranged by Arranger"
            instruments = "piano"
            license = "Creative Commons Attribution-ShareAlike 4.0"
        }"""

        self.test_score = Score(title='Test Score', slug='testscore')

        composer = Composer(name='Composer')
        composer.save()

        self.test_score.composer = composer

        arranger = Arranger(name='Arranger')
        arranger.save()

        self.test_score.arranger = arranger

        instrument = Instrument(name='Instrument')
        instrument.save()

        self.test_score.save()

        self.test_score.instruments.add(instrument)

