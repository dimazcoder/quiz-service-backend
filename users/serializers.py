from django.contrib.auth import get_user_model
from rest_framework import serializers
from attempters.models import Attempter

User = get_user_model()

class UserReadSerializer(serializers.ModelSerializer):
    attempter_id = serializers.PrimaryKeyRelatedField(source='attempter', read_only=False, queryset=Attempter.objects.all())
    class Meta:
        model = User
        exclude = ('password',)

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', )
