# Licensed under the MIT License

from django.test import TestCase

from scores.models import Arranger


class ArrangerTest(TestCase):
    def setUp(self):
        self.arranger = Arranger(name='Test Arranger')

    def test__eq__(self):
        self.assertEqual(Arranger(name='Test Arranger'), self.arranger)

    def test__hash__(self):
        expected_hash = hash((self.arranger.id, self.arranger.name))
        self.assertEqual(self.arranger.__hash__(), expected_hash)

    def test__str__(self):
        self.assertEqual(self.arranger.__str__(), 'Test Arranger')
