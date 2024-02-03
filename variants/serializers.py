from questions.models import Question
from rest_framework import serializers
from results.models import Result

from .models import Variant, VariantsGraph


class VariantCreateSerializer(serializers.ModelSerializer):
    # id нужно было прописать явно, чтобы он приходил из сериализатора при создании вопроса.
    # По дефолту в django он ReadOnlyField и не возвращается, когда сериализатор вложенный,
    # например, как варианты в вопросе
    id = serializers.ModelField(model_field=Variant()._meta.get_field('id'), required=False)
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    question_id = serializers.PrimaryKeyRelatedField(source='question', read_only=True)

    class Meta:
        model = Variant
        exclude = ('question', 'modified_user',)

class VariantUpdateSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Variant()._meta.get_field('id'), required=True)
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_deleted = serializers.BooleanField(default=False)

    class Meta:
        model = Variant
        exclude = ('question', 'created_user',)

class VariantSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    question_id = serializers.PrimaryKeyRelatedField(source='question', read_only=True)

    class Meta:
        model = Variant
        fields = '__all__'

class VariantWithoutQuestionSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Variant
        exclude = ('question',)

class VariantWithoutQuestionAndResultsSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Variant
        exclude = ('question', 'results', 'text_selected',)

class VariantsGraphQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()

class VariantsGraphResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    text = serializers.CharField()

class VariantsGraphSerializer(serializers.ModelSerializer):
    variant_id = serializers.PrimaryKeyRelatedField(source='variant', read_only=True)
    next_question = VariantsGraphQuestionSerializer()
    result = VariantsGraphResultSerializer()
    class Meta:
        model = VariantsGraph
        fields = '__all__'

class VariantsWithGraphSerializer(serializers.ModelSerializer):
    graph = VariantsGraphSerializer(default=None)

    class Meta:
        model = Variant
        fields = '__all__'

class VariantsGraphCreateOrUpdateSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=VariantsGraph()._meta.get_field('id'), required=False)
    variant_id = serializers.PrimaryKeyRelatedField(source='variant', read_only=False, queryset=Variant.objects.all())
    next_question_id = serializers.PrimaryKeyRelatedField(source='next_question', read_only=False, queryset=Question.objects.all(), allow_null=True)
    result_id = serializers.PrimaryKeyRelatedField(source='result', read_only=False, queryset=Result.objects.all(), allow_null=True)

    class Meta:
        model = VariantsGraph
        fields = ('id', 'variant_id', 'next_question_id', 'result_id',)

    def validate(self, attrs):
        return super().validate(attrs)
