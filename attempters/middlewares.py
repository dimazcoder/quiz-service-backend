# import json

import jwt
from attempters.services import get_attempter_by_id
# from customjwt import views
from django.conf import settings

# from django.http import HttpResponse
# from rest_framework import status


class CheckAttempterInJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Проверяет наличие JWT, разбирает его и достает оттуда attempter_id.
        # Проверяет наличие attempter в базе по этому идентификатору
        # и в случае его наличия пишет его в реквест.
        # В случае его отсутствия просто пропускает дальше реквест без attempter.
        if 'HTTP_AUTHORIZATION' in request.META:
            try:
                auth_header_type, token = request.META.get('HTTP_AUTHORIZATION', '').split()
            except ValueError:
                return None

            auth_header_types = settings.SIMPLE_JWT['AUTH_HEADER_TYPES']

            if auth_header_type in auth_header_types:
                try:
                    decoded_token_data = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
                except jwt.InvalidTokenError:
                    return None

                if 'attempter_id' in decoded_token_data:
                    attempter = get_attempter_by_id(decoded_token_data['attempter_id'])

                    if attempter:
                        request.attempter = attempter

        return None
