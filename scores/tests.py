from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

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

    def test_get_paths_to_pages_with_no_pages(self):
        score = Score(title='My Score', slug='myscore')
        paths_to_pages = score.get_paths_to_pages()

        self.assertIsNotNone(paths_to_pages)
        self.assertTrue(len(paths_to_pages) == 0)

    def test_path_to_pages_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        paths_to_pages = score.get_paths_to_pages()

        self.assertIsNotNone(paths_to_pages)
        self.assertTrue(len(paths_to_pages) == 0)

    def test_get_thumbnail_path(self):
        score = Score(title='My Score', slug='myscore')
        thumbnail_path = score.get_thumbnail_path()
        self.assertEqual(thumbnail_path, 'scores/myscore/thumbnail.png')

    def test_get_thumbnail_path_if_score_has_no_slug(self):
        score = Score(title='My Score', slug='')
        thumbnail_path = score.get_thumbnail_path()
        self.assertEqual(thumbnail_path, '')

    def test_source_link(self):
        score = Score(title="My Score", slug="myscore")
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere/tree/master/myscore/")

    def test_source_link_if_score_has_no_slug(self):
        score = Score(title="My Score", slug='')
        link = score.get_link_to_source()
        self.assertEqual(link, "https://github.com/dmitrvk/mymusichere")

    def test_source_link_if_github_repo_not_set(self):
        with self.settings(GITHUB_SCORES_SOURCE_REPO=None):
            score = Score(title='My Score', slug='myscore')
            link = score.get_link_to_source()
            self.assertEqual(link, 'https://github.com/')

    def test_update_with_score(self):
        score = Score(title='My Score', slug='myscore')
        score.composer = 'Composer'
        score.arranger = 'Arranger'
        score.instrument = 'Instrument'

        new_score = Score(title='New Score', slug='newscore')
        new_score.composer = 'New Composer'
        new_score.arranger = 'New Arranger'
        new_score.instrument = 'New Instrument'

        score.update_with_score(new_score)

        self.assertEqual(score.title, new_score.title)
        self.assertEqual(score.composer, new_score.composer)
        self.assertEqual(score.arranger, new_score.arranger)
        self.assertEqual(score.instrument, new_score.instrument)
        self.assertEqual(score.instrument, new_score.instrument)

    def test_eq(self):
        score_one = Score(title='My Score', slug='myscore')
        score_one.composer = 'Composer'
        score_one.arranger = 'Arranger'
        score_one.instrument = 'Instrument'

        score_two = Score(title='My Score', slug='myscore')
        score_two.composer = 'Composer'
        score_two.arranger = 'Arranger'
        score_two.instrument = 'Instrument'

        self.assertTrue(score_one == score_two)

    def test_str(self):
        score = Score(title='My Score', slug='myscore')
        score.composer = 'Composer'
        score.arranger = 'Arranger'
        score.instrument = 'Instrument'
        self.assertEqual(score.__str__(), 'myscore (My Score, Composer, Arranger, Instrument)')



class ScoreIndexViewTest(TestCase):

    def test_no_scores(self):
        client = Client()
        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No scores are available.')
