from attempters.services import create_attempter, get_attempter_for_user
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ 
    Переопределения сериализатора SimpleJWT, 
    чтобы можно было генерировать JWT для анрегов
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['password'].required = False

    def validate(self, attrs):
        if 'username' not in attrs:
            attrs.update({'username': ''})

        if 'password' not in attrs:
            attrs.update({'password': ''})

        return super(CustomTokenObtainPairSerializer, self).validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if isinstance(user, AnonymousUser):
            attempter = create_attempter()
            del token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        else:
            attempter = get_attempter_for_user(user_id=user.id)
        
            if not attempter:
                attempter = create_attempter(user=user)
        
        token['attempter_id'] = attempter.id

        return token
