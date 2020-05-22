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

    def test_get_method_not_allowed(self):
        response = self.client.get(reverse('scores:publish'))
        self.assertEqual(response.status_code, 405)

    @unittest.skip('must be corrected for new models')
    def test_wrong_request(self):
        response = self.client_no_auth.post(reverse('scores:publish'))
        self.assertEqual(response.status_code, 400)

    @unittest.skip('must be corrected for new models')
    def test_update_db_failed(self):
        method = PublishView._delete_scores_removed_from_repo
        mock = MagicMock(side_effect=Exception())

        PublishView._delete_scores_removed_from_repo = mock

        response = self.client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 500)

        PublishView._delete_scores_removed_from_repo = method

    @unittest.skip('must be corrected for new models')
    @patchfs
    def test_get_repo_scores(self, fs):
        repo_dir_path = os.path.join(settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores')

        fs.create_dir(repo_dir_path)

        for slug in self.test_slugs:
            score_path = os.path.join(repo_dir_path, slug)
            fs.create_dir(score_path)

        repo_scores = PublishView()._get_repo_scores()

        self.assertIsNotNone(repo_scores)
        self.assertIsInstance(repo_scores, set)
        self.assertEqual(repo_scores, self.test_slugs)

    @unittest.skip('must be corrected for new model')
    def test_get_db_scores(self):
        for slug in self.test_slugs:
            Score(title=slug, slug=slug).save()

        db_scores = PublishView()._get_db_scores()

        self.assertIsNotNone(db_scores)
        self.assertIsInstance(db_scores, set)
        self.assertEqual(db_scores, self.test_slugs)

    @unittest.skip('must be corrected for new models')
    @patchfs
    def test_create_score_from_header(self, fs):
        slug = 'new_testscore'

        filename = '{}.ly'.format(slug)
        path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, slug, filename)

        fs.create_file(path_to_source, contents=self.test_lilypond_header)

        score = PublishView()._create_score_from_header(slug)
        score.save()

        self.assertIsNotNone(score)
        self.assertIsInstance(score, Score)
        self.assertEquals(score.slug, slug)
        self.assertEquals(score.title, 'Test Score')
        self.assertIsNotNone(score.composer)
        self.assertEquals(score.composer.name, 'Composed by Composer')
        self.assertIsNotNone(score.arranger)
        self.assertEquals(score.arranger.name, 'Arranged by Arranger')
        self.assertIsNotNone(score.instruments)
        self.assertEquals(score.instruments.all().count(), 0)

    def test_request_valid(self):
        request = HttpRequest()
        request.headers = {'Authorization': self.auth_token}

        self.assertTrue(PublishView()._is_request_valid(request))

    def test_request_invalid(self):
        request = HttpRequest()

        self.assertFalse(PublishView()._is_request_valid(request))

    @patchfs
    @unittest.skip('must be corrected for new model')
    def test_one_score_created(self, fs):
        slug = 'testscore'

        filename = f'{slug}.ly'
        path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, slug, filename)
        fs.create_file(path_to_source, contents=self.test_lilypond_header)

        pages_dir_path = os.path.join(settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores', slug)
        fs.create_dir(pages_dir_path)

        response = self.client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 200)

        scores = Score.objects.all()

        self.assertEqual(len(scores), 1)

        score = scores[0]

        self.assertIsNotNone(score)
        self.assertIsInstance(score, Score)
        self.assertEquals(score.slug, slug)
        self.assertEquals(score.title, 'Test Score')
        self.assertIsNotNone(score.composer)
        self.assertEquals(score.composer.name, 'Composed by Composer')
        self.assertIsNotNone(score.arranger)
        self.assertEquals(score.arranger.name, 'Arranged by Arranger')
        self.assertIsNotNone(score.instruments)
        self.assertEquals(score.instruments.all().count(), 0)

    @patchfs
    @unittest.skip('must be corrected for new model')
    def test_one_score_deleted(self, fs):
        slug = 'testscore'

        Score(title='Test Score', slug=slug).save()

        self.assertEquals(len(Score.objects.all()), 1)

        filename = '{}.ly'.format(slug)
        path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, slug, filename)
        fs.create_file(path_to_source, contents=self.test_lilypond_header)

        pages_dir_path = os.path.join(settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores')
        fs.create_dir(pages_dir_path)

        response = self.client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(Score.objects.all()), 0)

    @patchfs
    @unittest.skip('must be corrected for new model')
    def test_update_one_score(self, fs):
        slug = self.test_score.slug

        self.assertEquals(len(Score.objects.all()), 1)

        filename = f'{slug}.ly'
        path_to_source = os.path.join(settings.MYMUSICHERE_REPO_DIR, slug, filename)
        fs.create_file(path_to_source, contents=self.test_lilypond_header)

        pages_dir_path = os.path.join(settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores', slug)
        fs.create_dir(pages_dir_path)

        response = self.client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 200)

        scores = Score.objects.all()

        self.assertEquals(len(scores), 1)

        score = scores[0]

        self.assertIsNotNone(score)
        self.assertIsInstance(score, Score)
        self.assertEqual(score.title, 'Test Score')
        self.assertIsNotNone(score.composer)
        self.assertEqual(score.composer.name, 'Composed by Composer')
        self.assertIsNotNone(score.arranger)
        self.assertEqual(score.arranger.name, 'Arranged by Arranger')
        self.assertEqual(score.instruments.all()[0].name, 'piano')
