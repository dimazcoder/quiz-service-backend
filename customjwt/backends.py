from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser


User=get_user_model()

class CustomJWTAuthenticationBackend(BaseBackend):
    """ 
    Аутентификация перед генерацией токена по креденшелам, которые передал юзер. 
    Если креденшелы не были переданы, то токен генерится для AnonymousUser 
    """
    def authenticate(self, request, username=None, password=None):
        if username and password:
            try:
                user = User.objects.get(username=username, password=password)
                # user.attempter – привязанный участник к пользователю
                # request.attempter – участник который был в токене при авторизации
            except User.DoesNotExist:
                user = None
        else:
            user = AnonymousUser()
            user.is_active = True

        return user

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = AnonymousUser()
            user.is_active = True
            
        return user
