from django.test import TestCase
from attempters.models import Attempter
from attempters.serializers import AttempterSerializer, AttempterSafeSerializer
from attempters.tests.setup import get_attempter_data

class AttempterSerializerTestCase(TestCase):
    def setUp(self):
        self.attempter_data = get_attempter_data()
        self.attempter = Attempter.objects.create(**self.attempter_data)
        self.serializer = AttempterSerializer(instance=self.attempter)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'email', 'phone_number', 'user', 'created_at', 'modified_at'})

    def test_serializer_valid_data(self):
        self.assertEqual(self.serializer.data['email'], self.attempter_data['email'])
        self.assertEqual(self.serializer.data['phone_number'], str(self.attempter_data['phone_number']))

class AttempterSafeSerializerTestCase(TestCase):
    def setUp(self):
        self.attempter_data = get_attempter_data()
        self.attempter = Attempter.objects.create(**self.attempter_data)
        self.serializer = AttempterSafeSerializer(instance=self.attempter)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(set(data.keys()), {'id', 'user', 'created_at', 'modified_at'})

    def test_serializer_valid_data(self):
        self.assertEqual(self.serializer.data['user'], None)

    def test_serializer_excludes_email_and_phone_number(self):
        self.assertNotIn('email', self.serializer.data)
        self.assertNotIn('phone_number', self.serializer.data)
