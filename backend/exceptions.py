from rest_framework import status
from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = 'Ошибка сервера.'

    def __init__(self, detail=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
