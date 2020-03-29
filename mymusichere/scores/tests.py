from django.test import TestCase

from .models import Score

class ScoreModelTest(TestCase):

    def test_filename(self):
        score = Score(title="My Score", slug="myscore")
        filename = score.get_filename()
        self.assertEqual(filename, 'myscore/myscore.pdf')

    def test_filename_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        filename = score.get_filename()
        self.assertEqual(filename, '')

    def test_source_link(self):
        score = Score(title="My Score", slug="myscore")
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere/tree/master/myscore/")

    def test_source_link_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere/")

