from rest_framework import serializers

from .models import Attempter


class AttempterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempter
        fields = '__all__'

class AttempterSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempter
        exclude = ('email', 'phone_number',)
