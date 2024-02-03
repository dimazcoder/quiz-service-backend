import random
from typing import List

from attempts.models import Attempt, AttemptQuestion
from attempts.services import get_asked_questions_for_attempter_in_quizz
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, QuerySet
from quizzes.models import Quizz
from quizzes.services import get_complexities_for_quizz

from .models import QUESSTION_GUESS_TYPE_ANY, Question

User = get_user_model()


def check_questions_existence_for_quizz(quizz_id: int) -> bool:
    """ Проверяет наличие вопросов для квиза """
    return Question.objects.filter(quizz_id=quizz_id).exists()

def get_questions_for_quizz(quizz_id: int) -> QuerySet[Question] | None:
    """ Получает список вопросов квиза по его идентификатору """
    try:
        return Question.objects.filter(quizz_id=quizz_id).order_by('sort_order')
    except Question.DoesNotExist:
        return None

def get_start_question_for_quizz(quizz_id: int) -> Question | None:
    """ Возвращает стартовый вопрос для квиза (используеся если тип квиза "квест") """
    return Question.objects.filter(quizz_id=quizz_id, is_start=True).first()

def prepare_questions_for_quizz(quizz: Quizz, attempter_id: int) -> List[Question]:
    """ Возвращает список вопросов для попытки в момент старта квиза  """
    quizz_questions = get_questions_for_quizz(quizz_id=quizz.id)
    quizz_complexities = get_complexities_for_quizz(quizz_id=quizz.id)

    asked_question_ids = []
    if quizz.is_random_questions:
        asked_questions = get_asked_questions_for_attempter_in_quizz(quizz_id=quizz.id, attempter_id=attempter_id)
        if asked_questions:
            asked_question_ids = asked_questions.values_list('id', flat=True)
    
    quizz_count_questions = quizz.count_questions if quizz.count_questions else quizz_questions.count()
    
    if quizz_complexities:
        complexities = []
        for quizz_complexity in quizz_complexities:
            complexities.append({
                'complexity': quizz_complexity.complexity,
                'quantity': quizz_complexity.quantity
            })
    else:
        complexities = [{
            'complexity': 1, 
            'quantity': quizz_count_questions
        }]

    prepared_quizz_questions = []
    for complexity in complexities:
        complexity_questions, complexity_asked_questions, complexity_not_asked_questions = [], [], []

        for quizz_question in quizz_questions:
            if quizz_question.complexity == complexity['complexity']:
                if quizz_question.id in asked_question_ids:
                    complexity_asked_questions.append(quizz_question)
                else:
                    complexity_not_asked_questions.append(quizz_question)

        if quizz.is_random_questions:
            random.shuffle(complexity_asked_questions)
            random.shuffle(complexity_not_asked_questions)

        complexity_questions = complexity_not_asked_questions[:complexity['quantity']] if len(complexity_not_asked_questions) > complexity['quantity'] else complexity_not_asked_questions
        
        if len(complexity_questions) < complexity['quantity']:
            complexity_questions.extend(complexity_asked_questions[:complexity['quantity']-len(complexity_questions)])

        prepared_quizz_questions += complexity_questions

    if len(prepared_quizz_questions) < quizz_count_questions:
        if quizz.is_random_questions:
            quizz_questions = list(quizz_questions)
            random.shuffle(quizz_questions)

        for quizz_question in quizz_questions:
            if quizz_question.id not in prepared_quizz_questions and len(prepared_quizz_questions) < quizz_count_questions:
                prepared_quizz_questions.append(quizz_question)

    return prepared_quizz_questions

def save_attempt_questions(attempt: Attempt, questions: List[Question]) -> None:
    """ Привязка вопросов к попытке (вызывается при создании попытки в ее сериализаторе) """
    AttemptQuestion.objects.bulk_create([AttemptQuestion(attempt=attempt, question=question, sort_order=(key+1)) for key, question in enumerate(questions)])

def create_question(
    text: str, 
    quizz: Quizz, 
    created_user: User, 
    correct_text: str = '', 
    incorrect_text: str = '', 
    partially_correct_text: str = '', 
    guess_type: int = QUESSTION_GUESS_TYPE_ANY, 
    sort_order: int = 0, 
    complexity: int = 1, 
    is_start: bool = False) -> Question:
    """ Создание вопроса """
    quiestion = Question.objects.create(
        text=text,
        correct_text=correct_text,
        incorrect_text=incorrect_text,
        partially_correct_text=partially_correct_text,
        quizz=quizz,
        created_user=created_user,
        modified_user=created_user,
        guess_type=guess_type,
        sort_order=sort_order,
        complexity=complexity,
        is_start=is_start
    )
    
    return quiestion

def get_question_for_quizz_by_id(quizz_id: int, question_id: int) -> Question | None:
    """ Возвращает стартовый вопрос для квиза (используеся если тип квиза "квест") """
    return Question.objects.filter(pk=question_id, quizz_id=quizz_id).first()

def get_questions_with_varitants_without_graph_for_quizz(quizz_id: int) -> QuerySet[Question] | None:
    """ Получение списка вопросов, варианты которых не содержат графа """
    try: 
        return Question.objects.all().filter(quizz_id=quizz_id).filter(Q(variants__graph__isnull=True)).annotate(count_variants=Count('variants__id'))
    except Question.DoesNotExist:
        return None
    
def get_previous_graph_questions_for_question(question_id: int) -> QuerySet[QuerySet] | None:
    """ Получение вопросов, ваианты которых ведут к этому вопросу в квизе с типом "Квест" """
    try:
        return Question.objects.filter(variants__graph__next_question_id=question_id)
    except Question.DoesNotExist:
        return None

