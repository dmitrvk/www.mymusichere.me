from django.test import Client, TestCase

from scores.models import Score


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_scores(self):
        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No scores are available.')

    def test_one_score(self):
        score = Score(title='Test Score', slug='testscore')
        score.save()

        response = self.client.get(reverse('scores:index'))

        self.assertEqual(response.status_code, 200)

        scores = response.context.get('score_list', None)

        self.assertIsNotNone(scores)
        self.assertEqual(len(scores), 1)
        self.assertEqual(scores[0], score)
