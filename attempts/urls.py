from django.urls import path

from . import views


urlpatterns = [
    path('', views.AttemptModelViewSet.as_view({'post': 'create'})),
    path('<int:pk>/', views.AttemptModelViewSet.as_view({'get': 'retrieve'})),
    path('<str:guid>/', views.AttemptModelViewSet.as_view({'get': 'retrieve'})),
    path('<int:attempt_id>/questions/', views.AttemptQuestionModelViewSet.as_view({'get': 'list'})),
    path('<int:attempt_id>/questions/<int:sort_order>/', views.AttemptQuestionModelViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
]
