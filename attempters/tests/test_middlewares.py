import jwt
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.conf import settings
from attempters.middlewares import CheckAttempterInJWTMiddleware
from attempters.models import Attempter
from attempters.tests.setup import get_attempter

class CheckAttempterInJWTMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # self.user = get_user_model().objects.create(username='testuser')
        # self.attempter = Attempter.objects.create(email='test@example.com', phone_number='+1234567890', user=self.user)
        self.attempter = get_attempter()
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.SIMPLE_JWT['ALGORITHM']
        self.valid_token = self.generate_token({'attempter_id': self.attempter.id})
        self.invalid_token = 'invalid_token'

    def generate_token(self, payload):
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def test_middleware_valid_token(self):
        request = self.factory.get('/api/dumb-endpoint/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.valid_token}'
        middleware = CheckAttempterInJWTMiddleware(self._dummy_response)
        middleware_response = middleware(request)
        if middleware_response is not None:
            self.assertEqual(middleware_response.status_code, 200)
            self.assertEqual(request.attempter, self.attempter)

    def test_middleware_invalid_token(self):
        request = self.factory.get('/api/dumb-endpoint/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.invalid_token}'
        middleware = CheckAttempterInJWTMiddleware(self._dummy_response)
        middleware_response = middleware(request)
        self.assertEqual(middleware_response, None)
        self.assertFalse(hasattr(request, 'attempter'))

    def _dummy_response(self, request):
        return None
