from django.test import TestCase, Client
from django.urls import reverse

from .models import Score

class ScoreModelTest(TestCase):

    def test_path_to_pdf(self):
        score = Score(title="My Score", slug="myscore")
        filename = score.get_path_to_pdf()
        self.assertEqual(filename, 'scores/myscore/myscore.pdf')

    def test_path_to_pdf_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        filename = score.get_path_to_pdf()
        self.assertEqual(filename, '')

    def test_source_link(self):
        score = Score(title="My Score", slug="myscore")
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere/tree/master/myscore/")

    def test_source_link_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere/")


class ScoreIndexViewTest(TestCase):

    def test_no_scores(self):
        client = Client()
        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No scores are available.')
