import copy
import os
import unittest

from django.conf import settings
from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse

from pyfakefs.fake_filesystem_unittest import patchfs
from unittest.mock import MagicMock

from .models import Arranger, Composer, Instrument, Score
from .views import PublishView


class ScoreModelTest(TestCase):
    def setUp(self):
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

        self.test_score_no_slug = Score(title='Test Score', slug='')

    def test_get_pdf_path(self):
        filename = self.test_score.get_pdf_path()
        expected = 'scores/{slug}/{slug}.pdf'.format(slug=self.test_score.slug)
        self.assertEqual(filename, expected)

    def test_get_pdf_path_no_slug(self):
        filename = self.test_score_no_slug.get_pdf_path()
        self.assertEqual(filename, '')

    @patchfs
    def test_get_pages_paths(self, fs):
        pages_dir_path = os.path.join(
            settings.STATIC_ROOT, 'scores', self.test_score.slug
        )

        expected_paths = []

        for i in range(3):
            filename = '{slug}-page{number}.png'.format(
                slug=self.test_score.slug,
                number=i
            )

            page_path = os.path.join(pages_dir_path, filename)

            fs.create_file(page_path)

            expected_paths.append(os.path.join(
                'scores', self.test_score.slug, filename
            ))

        actual_paths = self.test_score.get_pages_paths()

        self.assertIsNotNone(actual_paths)
        self.assertEquals(len(actual_paths), len(expected_paths))

        for i, expected_path in enumerate(expected_paths):
            self.assertEquals(actual_paths[i], expected_path)

    def test_get_pages_paths_with_no_pages(self):
        paths = self.test_score.get_pages_paths()

        self.assertIsNotNone(paths)
        self.assertIsInstance(paths, list)
        self.assertTrue(len(paths) == 0)

    def test_get_pages_paths_if_score_has_no_slug(self):
        paths = self.test_score_no_slug.get_pages_paths()

        self.assertIsNotNone(paths)
        self.assertIsInstance(paths, list)
        self.assertTrue(len(paths) == 0)

    def test_get_thumbnail_path(self):
        expected_path = 'scores/{slug}/thumbnail.png'.format(
            slug=self.test_score.slug
        )

        actual_path = self.test_score.get_thumbnail_path()

        self.assertEqual(actual_path, expected_path)

    def test_get_thumbnail_path_of_score_without_slug(self):
        path = self.test_score_no_slug.get_thumbnail_path()
        self.assertEqual(path, '')

    def test_get_link_to_source(self):
        expected_link = '{repo}/tree/master/{slug}'.format(
            repo=settings.GITHUB_SCORES_SOURCE_REPO,
            slug=self.test_score.slug
        )

        actual_link = self.test_score.get_link_to_source()

        self.assertEqual(actual_link, expected_link)

    def test_get_link_to_source_of_score_without_slug(self):
        link = self.test_score_no_slug.get_link_to_source()
        self.assertEqual(link, settings.GITHUB_SCORES_SOURCE_REPO)

    def test_get_link_to_source_if_repo_not_set(self):
        with self.settings(GITHUB_SCORES_SOURCE_REPO=None):
            link = self.test_score.get_link_to_source()
            self.assertEqual(link, 'https://github.com/')

    def test_eq(self):
        score_one = copy.copy(self.test_score)
        score_two = copy.copy(self.test_score)

        self.assertTrue(score_one == score_two)

    def test_str(self):
        expected = '{slug} ({title})'.format(
            slug=self.test_score.slug,
            title=self.test_score.title,
        )

        self.assertEqual(self.test_score.__str__(), expected)

    def test_hash(self):
        expected = hash((self.test_score.id, self.test_score.title))
        self.assertEqual(self.test_score.__hash__(), expected)


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

        pages_paths = response_score.get_pages_paths()

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

    def test_wrong_request(self):
        response = self.client_no_auth.post(reverse('scores:publish'))
        self.assertEqual(response.status_code, 400)

    def test_update_db_failed(self):
        method = PublishView._delete_scores_removed_from_repo
        mock = MagicMock(side_effect=Exception())

        PublishView._delete_scores_removed_from_repo = mock

        response = self.client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 500)

        PublishView._delete_scores_removed_from_repo = method

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
