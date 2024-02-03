from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets

from backend.exceptions import CustomAPIException
from backend.permissions import IsAttempter

from .models import Attempt, AttemptQuestion
from .permissions import IsAttemptOwner, IsQuestionAttemptOwner
from .serializers import (AttemptQuestionSerializer,
                          AttemptQuestionUpdateSerializer,
                          AttemptSafeSerializer, AttemptSerializer)
from .services import get_attempt_by_id


class AttemptModelViewSet(viewsets.ModelViewSet):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer
    permission_classes = [IsAttempter, ]

    def get_permissions(self):
        if self.action == 'retrieve' and 'id' in self.kwargs:
            self.permission_classes = [IsAttempter, IsAttemptOwner, ]
        else:
            self.permission_classes = [IsAttempter,]

        return super(AttemptModelViewSet, self).get_permissions()
    
    def get_object(self):
        guid = self.kwargs.get('guid', None)
        if guid:
            return get_object_or_404(Attempt, guid=guid)
        return super(AttemptModelViewSet, self).get_object()
    
    def get_serializer_class(self):
        # Для просмотра страницы результата попытки, 
        # чтобы не светить лишней информацией участника анрегам
        if self.action == 'retrieve' and 'guid' in self.kwargs:
            return AttemptSafeSerializer
        
        return self.serializer_class

class AttemptQuestionModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsQuestionAttemptOwner, ]
    lookup_fields = ['attempt_id', 'sort_order']

    def get_object(self):
        return get_object_or_404(self.get_queryset(), sort_order=self.kwargs['sort_order'])

    def get_queryset(self):
        attempt_id = self.kwargs['attempt_id']
        return AttemptQuestion.objects.filter(attempt_id=attempt_id)

    def partial_update(self, request, *args, **kwargs):
        attempt = get_attempt_by_id(attempt_id=kwargs['attempt_id'])

        if attempt.results.all():
            raise CustomAPIException(detail='Нельзя отвечать на вопросы закрытой попытки.', status_code=status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ['PATCH']:
            return AttemptQuestionUpdateSerializer
        else:
            return AttemptQuestionSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'attempt_id': self.kwargs['attempt_id']})
        if self.request.method in ['PATCH']:
            context.update({'attempt_question_sort_order': self.kwargs['sort_order']})
        return context
