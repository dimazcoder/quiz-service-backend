from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from attempters.models import Attempter
from attempters.serializers import AttempterSerializer
from attempters.tests.setup import get_attempter_data, get_invalid_attempter_data, get_updated_attempter_data

class AttempterViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # self.user = get_user_model().objects.create(username='testuser')
        self.attempter_data = get_attempter_data()
        self.attempter = Attempter.objects.create(**self.attempter_data)
        self.invalid_attempter_data = get_invalid_attempter_data()
        self.url_list = reverse('attempter-list')
        self.url_detail = reverse('attempter-detail', args=[self.attempter.id])

    def test_create_attempter(self):
        response = self.client.post(self.url_list, self.attempter_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_attempter(self):
        response = self.client.post(self.url_list, self.invalid_attempter_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_attempter_list(self):
        response = self.client.get(self.url_list)
        attempters = Attempter.objects.all()
        serializer = AttempterSerializer(attempters, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_attempter_detail(self):
        response = self.client.get(self.url_detail)
        serializer = AttempterSerializer(self.attempter)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_attempter(self):
        updated_data = get_updated_attempter_data()
        response = self.client.put(self.url_detail, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.attempter.refresh_from_db()
        self.assertEqual(self.attempter.email, updated_data['email'])
        self.assertEqual(str(self.attempter.phone_number), updated_data['phone_number'])

    def test_delete_attempter(self):
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Attempter.objects.filter(id=self.attempter.id).exists())
