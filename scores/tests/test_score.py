# Licensed under the MIT License

import copy
import os

from pyfakefs.fake_filesystem_unittest import patchfs

from django.conf import settings
from django.test import TestCase
from scores.models import Arranger, Composer, Instrument, Score


class ScoreTest(TestCase):
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

    def test_pdf_path(self):
        filename = self.test_score.pdf_path
        expected = '{slug}/{slug}.pdf'.format(slug=self.test_score.slug)
        self.assertEqual(filename, expected)

    def test_pdf_path_no_slug(self):
        filename = self.test_score_no_slug.pdf_path
        self.assertEqual(filename, '')

    @patchfs
    def test_pages_paths(self, fs):
        pages_dir_path = os.path.join(
            settings.BASE_DIR, 'static', 'scores', self.test_score.slug
        )

        expected_paths = []

        for i in range(3):
            filename = '{slug}-page{number}.png'.format(
                slug=self.test_score.slug,
                number=i
            )

            page_path = os.path.join(pages_dir_path, filename)
            fs.create_file(page_path)

            expected_paths.append(os.path.join(self.test_score.slug, filename))

        actual_paths = self.test_score.pages_paths

        self.assertIsNotNone(actual_paths)
        self.assertEquals(len(actual_paths), len(expected_paths))

        for i, expected_path in enumerate(expected_paths):
            self.assertEquals(actual_paths[i], expected_path)

    def test_pages_paths_no_pages(self):
        paths = self.test_score.pages_paths

        self.assertIsNotNone(paths)
        self.assertIsInstance(paths, list)
        self.assertTrue(len(paths) == 0)

    def test_pages_paths_no_slug(self):
        paths = self.test_score_no_slug.pages_paths

        self.assertIsNotNone(paths)
        self.assertIsInstance(paths, list)
        self.assertTrue(len(paths) == 0)

    def test_thumbnail_path(self):
        expected_path = '{slug}/{slug}-thumbnail.png'.format(
            slug=self.test_score.slug
        )

        actual_path = self.test_score.thumbnail_path

        self.assertEqual(actual_path, expected_path)

    def test_thumbnail_path_no_slug(self):
        path = self.test_score_no_slug.thumbnail_path
        self.assertEqual(path, '')

    def test_github_link(self):
        expected_link = '{repo}/tree/master/{slug}'.format(
            repo=settings.GITHUB_SCORES_SOURCE_REPO,
            slug=self.test_score.slug
        )

        actual_link = self.test_score.github_link

        self.assertEqual(actual_link, expected_link)

    def test_github_link_no_slug(self):
        link = self.test_score_no_slug.github_link
        self.assertEqual(link, settings.GITHUB_SCORES_SOURCE_REPO)

    def test_github_link_no_repo(self):
        with self.settings(GITHUB_SCORES_SOURCE_REPO=None):
            link = self.test_score.github_link
            self.assertEqual(link, 'https://github.com/')

    def test__eq__(self):
        score_one = copy.copy(self.test_score)
        score_two = copy.copy(self.test_score)

        self.assertTrue(score_one == score_two)

    def test__hash__(self):
        expected = hash((self.test_score.id, self.test_score.title))  # pylint: disable=no-member  # noqa: E501
        self.assertEqual(self.test_score.__hash__(), expected)

    def test__str__(self):
        expected = '{slug} ({title})'.format(
            slug=self.test_score.slug,
            title=self.test_score.title,
        )

        self.assertEqual(self.test_score.__str__(), expected)
