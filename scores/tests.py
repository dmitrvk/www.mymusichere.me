from unittest.mock import MagicMock
import os

from django.http import HttpRequest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

from pyfakefs.fake_filesystem_unittest import patchfs

from django.conf import settings
from .models import Score
from .views import PublishView

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

    @patchfs
    def test_get_paths_to_pages(self, fs):
        score = Score(title='My Score', slug='myscore')

        pages_dir_parts = [settings.STATIC_ROOT, 'scores', 'myscore']
        pages_dir = os.path.join(*pages_dir_parts)

        pages_paths = []

        for i in range(3):
            page_filename = 'myscore-page%d.png' % (i + 1)
            page_path = os.path.join(pages_dir, page_filename)
            fs.create_file(page_path)
            pages_paths.append(page_path)

        score_pages_paths = score.get_paths_to_pages()

        self.assertIsNotNone(pages_paths)
        self.assertEquals(len(score_pages_paths), 3)

        for i, path in enumerate(pages_paths):
            self.assertTrue(score_pages_paths[i], path)

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

    def test_hash(self):
        score = Score(title='My Score', slug='myscore')
        score.save()
        self.assertEqual(score.__hash__(), hash((score.id, score.title)))



class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_no_scores(self):
        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No scores are available.')

    def test_one_score(self):
        score = Score(title='My Score', slug='myscore')
        score.save()

        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)

        scores = response.context.get('score_list', None)
        self.assertIsNotNone(scores)
        self.assertEqual(len(scores), 1)
        self.assertTrue(scores[0] == score)


class ScoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_view_score(self):
        score = Score(title='My Score', slug='myscore')
        score.save()

        response = self.client.get(reverse('scores:score', args=['myscore']))
        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)
        self.assertIsNotNone(response_score)
        self.assertTrue(response_score == score)

    def test_no_pages(self):
        score = Score(title='My Score', slug='myscore')
        score.save()

        response = self.client.get(reverse('scores:score', args=['myscore']))
        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)
        self.assertIsNotNone(response_score)

        paths_to_pages = response_score.get_paths_to_pages()
        self.assertEqual(len(paths_to_pages), 0)

        self.assertContains(response, 'Sorry, sheet music for this piece is not available.')

    def test_increment_views(self):
        score = Score(title='My Score', slug='myscore')
        self.assertEquals(score.views, 0)
        score.save()

        response = self.client.get(reverse('scores:index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('scores:score', args=['myscore']))
        self.assertEqual(response.status_code, 200)

        response_score = response.context.get('score', None)
        self.assertIsNotNone(response_score)
        self.assertIsInstance(response_score, Score)
        self.assertEquals(response_score.views, 1)



class PublishViewTest(TestCase):
    def test_publish_get_method(self):
        response = self.client.get(reverse('scores:publish'))
        self.assertEqual(response.status_code, 405)

    def test_publish_request_invalid(self):
        response = self.client.post(reverse('scores:publish'))
        self.assertEqual(response.status_code, 400)

    def test_update_db_failed(self):
        method = PublishView._PublishView__delete_scores_removed_from_repo

        mock = MagicMock(side_effect=Exception('BOOM!'))
        PublishView._PublishView__delete_scores_removed_from_repo = mock

        client = Client(HTTP_AUTHORIZATION='Token %s' % settings.PUBLISH_TOKEN)
        response = client.post(reverse('scores:publish'))
        self.assertEqual(response.status_code, 500)

        PublishView._PublishView__delete_scores_removed_from_repo = method

    @patchfs
    def test_get_repo_scores(self, fs):
        scores_dir_path_parts = [settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores']
        repo_dir = os.path.join(*scores_dir_path_parts)

        fs.create_dir(repo_dir)

        scores = {'myscore1', 'myscore2', 'myscore3'}

        for score in scores:
            fs.create_dir(os.path.join(repo_dir, score))

        repo_scores = PublishView()._PublishView__get_repo_scores()

        self.assertIsInstance(repo_scores, set)
        self.assertEqual(scores, repo_scores)

    def test_get_db_scores(self):
        scores = {'myscore1', 'myscore2', 'myscore3'}

        for slug in scores:
            Score(title=slug, slug=slug).save()

        db_scores = PublishView()._PublishView__get_db_scores()

        self.assertIsInstance(db_scores, set)
        self.assertEqual(scores, db_scores)

    @patchfs
    def test_create_score_from_header(self, fs):
        slug = 'myscore'
        path_to_source_parts = [settings.MYMUSICHERE_REPO_DIR, slug, '%s.ly' % slug]
        path_to_source = os.path.join(*path_to_source_parts)

        lilypond_header = """
        \header {
            title = "My Score"
            subtitle = "Subtitle"
            composer = "Composed by composer"
            arranger = "Arranged by arranger"
            instruments = "piano"
            license = "Creative Commons Attribution-ShareAlike 4.0"
        }"""

        fs.create_file(path_to_source, contents=lilypond_header)

        score = PublishView()._PublishView__create_score_from_header(slug)

        self.assertIsInstance(score, Score)
        self.assertEquals(score.slug, slug)
        self.assertEquals(score.title, 'My Score')
        self.assertEquals(score.composer, 'Composed by composer')
        self.assertEquals(score.arranger, 'Arranged by arranger')
        self.assertEquals(score.instrument, 'piano')

    def test_is_request_valid(self):
        publishView = PublishView()
        request = HttpRequest()

        valid = publishView._PublishView__is_request_valid(request)
        self.assertFalse(valid)

        headers = {'Authorization': 'Token %s' % settings.PUBLISH_TOKEN}
        request.headers = headers

        valid = publishView._PublishView__is_request_valid(request)
        self.assertTrue(valid)

    @patchfs
    def test_created_one_score(self, fs):
        slug = 'myscore'
        path_to_source_parts = [settings.MYMUSICHERE_REPO_DIR, slug, '%s.ly' % slug]
        path_to_source = os.path.join(*path_to_source_parts)

        lilypond_header = """
        \header {
            title = "My Score"
            subtitle = "Subtitle"
            composer = "Composed by composer"
            arranger = "Arranged by arranger"
            instruments = "piano"
            license = "Creative Commons Attribution-ShareAlike 4.0"
        }"""

        fs.create_file(path_to_source, contents=lilypond_header)

        path_to_out_dir_parts = [settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores', slug]
        path_to_out_dir = os.path.join(*path_to_out_dir_parts)

        fs.create_dir(path_to_out_dir)

        client = Client(HTTP_AUTHORIZATION='Token %s' % settings.PUBLISH_TOKEN)
        response = client.post(reverse('scores:publish'))
        self.assertEqual(response.status_code, 200)

        scores = Score.objects.all()
        self.assertEqual(len(scores), 1)

        score = scores[0]
        self.assertEqual(score.slug, slug)
        self.assertEqual(score.title, "My Score")
        self.assertEqual(score.composer, "Composed by composer")
        self.assertEqual(score.arranger, "Arranged by arranger")
        self.assertEqual(score.instrument, "piano")

    @patchfs
    def test_deleted_one_score(self, fs):
        Score(title='My Score', slug='myscore').save()
        self.assertEquals(len(Score.objects.all()), 1)

        path_to_source_parts = [settings.MYMUSICHERE_REPO_DIR, 'myscore', 'myscore.ly']
        path_to_source = os.path.join(*path_to_source_parts)
        lilypond_header = """
        \header {
            title = "My Score"
            subtitle = "Subtitle"
            composer = "Composed by composer"
            arranger = "Arranged by arranger"
            instruments = "piano"
            license = "Creative Commons Attribution-ShareAlike 4.0"
        }"""
        fs.create_file(path_to_source, contents=lilypond_header)

        path_to_out_dir_parts = [settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores']
        path_to_out_dir = os.path.join(*path_to_out_dir_parts)
        fs.create_dir(path_to_out_dir)

        client = Client(HTTP_AUTHORIZATION='Token %s' % settings.PUBLISH_TOKEN)
        response = client.post(reverse('scores:publish'))

        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(Score.objects.all()), 0)

    @patchfs
    def test_update_one_score(self, fs):
        score = Score(title='My Score', slug='myscore')
        score.composer = 'Composer'
        score.arranger = 'Arranger'
        score.instrument = 'guitar'
        score.save()
        self.assertEquals(len(Score.objects.all()), 1)

        path_to_source_parts = [settings.MYMUSICHERE_REPO_DIR, 'myscore', 'myscore.ly']
        path_to_source = os.path.join(*path_to_source_parts)
        lilypond_header = """
        \header {
            title = "My Score"
            subtitle = "Subtitle"
            composer = "Composed by composer"
            arranger = "Arranged by arranger"
            instruments = "piano"
            license = "Creative Commons Attribution-ShareAlike 4.0"
        }"""
        fs.create_file(path_to_source, contents=lilypond_header)

        path_to_out_dir_parts = [settings.BASE_DIR, 'scores', 'lilypond', 'out', 'scores', 'myscore']
        path_to_out_dir = os.path.join(*path_to_out_dir_parts)
        fs.create_dir(path_to_out_dir)

        client = Client(HTTP_AUTHORIZATION='Token %s' % settings.PUBLISH_TOKEN)
        response = client.post(reverse('scores:publish'))

        print(response.content)

        self.assertEqual(response.status_code, 200)

        scores = Score.objects.all()
        self.assertEquals(len(scores), 1)

        score = scores[0]
        self.assertIsInstance(score, Score)
        self.assertEqual(score.title, "My Score")
        self.assertEqual(score.composer, "Composed by composer")
        self.assertEqual(score.arranger, "Arranged by arranger")
        self.assertEqual(score.instrument, "piano")
