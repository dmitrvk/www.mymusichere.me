from django.test import Client, TestCase
from django.urls import reverse

from scores.models import Score


class ScoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_score = Score(title='Test Score', slug='testscore')
        self.test_score.save()

    def test_view_score(self):
        response = self.client.get(reverse('scores:score', args=[self.test_score.slug]))

        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)

        self.assertIsNotNone(response_score)
        self.assertIsInstance(response_score, Score)
        self.assertEqual(response_score, self.test_score)

    def test_no_pages(self):
        response = self.client.get(reverse('scores:score', args=[self.test_score.slug]))

        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)

        self.assertIsNotNone(response_score)
        self.assertIsInstance(response_score, Score)

        pages_paths = response_score.pages_paths

        self.assertEqual(len(pages_paths), 0)
        self.assertContains(response, 'Sorry, sheet music for this piece is not available.')

    def test_increment_views(self):
        self.assertEquals(self.test_score.views, 0)

        response = self.client.get(reverse('scores:index'))

        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('scores:score', args=[self.test_score.slug]))

        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)

        self.assertIsNotNone(response_score)
        self.assertIsInstance(response_score, Score)
        self.assertEquals(response_score.views, 1)
