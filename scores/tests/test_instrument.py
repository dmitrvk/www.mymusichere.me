# Licensed under the MIT License

from django.test import TestCase

from scores.models import Instrument


class InstrumentModelTest(TestCase):
    def setUp(self):
        self.instrument = Instrument(name='Test Instrument')

    def test__eq__(self):
        self.assertEqual(Instrument(name='Test Instrument'), self.instrument)

    def test__hash__(self):
        expected_hash = hash((self.instrument.id, self.instrument.name))
        self.assertEqual(self.instrument.__hash__(), expected_hash)

    def test__str__(self):
        self.assertEqual(self.instrument.__str__(), 'Test Instrument')
