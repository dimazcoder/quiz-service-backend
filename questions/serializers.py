from questions.services import get_previous_graph_questions_for_question
from quizzes.common_serializers import QuizzRelatedSerializer
from quizzes.models import Quizz
from rest_framework import serializers
from variants.serializers import (VariantCreateSerializer, VariantSerializer,
                                  VariantsWithGraphSerializer,
                                  VariantUpdateSerializer,
                                  VariantWithoutQuestionAndResultsSerializer)
from variants.services import (create_variant, get_variant_by_id,
                               remove_variant, remove_variants_for_question,
                               update_variant)

from .models import Question
from .services import create_question


class QuestionCreateSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.all())
    quizz_id = QuizzRelatedSerializer(source='quizz', read_only=False, queryset=Quizz.objects.none())
    variants = VariantCreateSerializer(many=True)

    class Meta:
        model = Question
        read_only_fields = ('quizz',)
        exclude = ('modified_user',)

    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        question = create_question(**validated_data)
        
        for variant_data in variants_data:
            # Можно было бы переписать на один запрос чрез bulk_create, но, как оказалось, только Postgresql умеет 
            # после их внесенеия списком возвращать id записей, а иначе не привяжешь m2m сущности в виде вопросов.
            # Писать через raw запрос - плохая практика и все равно будут лишние запросы
            variant_id = variant_data.get('id', None)
            variant = get_variant_by_id(variant_id) if variant_id else None
            variant_results = variant_data.pop('results') if 'results' in variant_data else None

            # При создании вопроса можно как создать новый вариант и он будет привязан к создаваемому вопросу, 
            # так и передать список уже созданных вариантов
            # 
            # Скорее всего, в дальнейшем убер отсюда это всё и сделаю отдельные эндпоинты для управления самими вариантами,
            # а здесь будет просто передаваться список уже сохраненных вариантов 
            if variant:
                variant_data.update({'question': question})
                update_variant(variant=variant, variant_data=variant_data, results=variant_results)
            else:
                create_variant(**variant_data, question=question, results=variant_results)

        return question

class QuestionUpdateSerializer(serializers.ModelSerializer):
    modified_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    variants = VariantUpdateSerializer(many=True)

    class Meta:
        model = Question
        exclude = ('quizz', 'created_user',)

    def update(self, instance, validated_data):
        
        variants_data = validated_data.pop('variants')

        if not self.partial and not variants_data:
            # Удалить все варианты ответов у вопроса если это PUT запрос и пустой список вариантов пришел с клиента
            remove_variants_for_question(question_id=instance.id)
        else:
            for variant_data in variants_data:
                variant_id = variant_data.pop('id') if 'id' in variant_data else None
                variant_results = variant_data.pop('results') if 'results' in variant_data else None

                variant = get_variant_by_id(variant_id=variant_id) if variant_id else None
                is_deleted = variant_data.pop('is_deleted') if 'is_deleted' in variant_data else False

                if variant and is_deleted:
                    remove_variant(variant_id=variant_id)
                else:
                    if variant:
                        variant_data.update({'question': instance})
                        update_variant(variant=variant, variant_data=variant_data, results=variant_results)
                    else:
                        created_user = variant_data.pop('modified_user') if 'modified_user' in variant_data else self.context['request'].user
                        variant_data['created_user'] = created_user
                        create_variant(**variant_data, question=instance, results=variant_results)

        instance = super().update(instance, validated_data)
        
        return instance

class QuestionSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.all())
    variants = VariantSerializer(many=True)
    count_variants_with_result = serializers.SerializerMethodField('get_count_variants_with_result')
    count_variants_with_score = serializers.SerializerMethodField('get_count_variants_with_score')

    def get_count_variants_with_result(self, instance):
        return instance.count_variants_with_result
    
    def get_count_variants_with_score(self, instance):
        return instance.count_variants_with_score

    class Meta:
        model = Question
        read_only_fields = ('quizz',)
        fields = '__all__'

class QuestionAttemptSerializer(serializers.ModelSerializer):
    created_user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.all())
    variants = VariantWithoutQuestionAndResultsSerializer(many=True)
    count_variants_with_result = serializers.SerializerMethodField('get_count_variants_with_result')
    count_variants_with_score = serializers.SerializerMethodField('get_count_variants_with_score')

    def get_count_variants_with_result(self, instance):
        return instance.count_variants_with_result
    
    def get_count_variants_with_score(self, instance):
        return instance.count_variants_with_score

    class Meta:
        model = Question
        read_only_fields = ('quizz',)
        fields = '__all__'

class QuestionGraphSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quizz_id = serializers.PrimaryKeyRelatedField(source='quizz', read_only=False, queryset=Quizz.objects.all())
    text = serializers.CharField()
    variants = VariantsWithGraphSerializer(many=True)
    previous_questions = serializers.SerializerMethodField('get_previous_questions')

    def get_previous_questions(self, instance):
        questions = get_previous_graph_questions_for_question(question_id=instance.pk)
        return QuestionSerializer(questions, many=True).data if questions else None
