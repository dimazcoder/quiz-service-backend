from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings


class CustomJWTAuthentication(JWTAuthentication):
    """ 
    Кастомная аутентификация, которая позволяет пропускать анрегов 
    с пустым user_id при наличии токена 
    """
    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            user_id = None

        if user_id:
            try:
                user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
            except self.user_model.DoesNotExist:
                raise AuthenticationFailed('Пользователь не найден', code='user_not_found')

            if not user.is_active:
                raise AuthenticationFailed('Пользователь неактивен', code='user_inactive')
        else:
            user = AnonymousUser()

        return user
        