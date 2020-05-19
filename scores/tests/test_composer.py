from django.test import TestCase

from scores.models import Composer


class ComposerModelTest(TestCase):
    def setUp(self):
        self.composer = Composer(name='Test Composer')

    def test__eq__(self):
        self.assertEqual(Composer(name='Test Composer'), self.composer)

    def test__hash__(self):
        expected_hash = hash((self.composer.id, self.composer.name))
        self.assertEqual(self.composer.__hash__(), expected_hash)

    def test__str__(self):
        self.assertEqual(self.composer.__str__(), 'Test Composer')
