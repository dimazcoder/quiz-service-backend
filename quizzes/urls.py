from django.urls import path

from . import views


urlpatterns = [
    path('', views.QuizzModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', views.QuizzModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('<str:alias>/', views.QuizzModelViewSet.as_view({'get': 'retrieve'})),
    path('<int:pk>/questionsgraph/', views.QuizzModelViewSet.as_view({'get': 'get_questionsgraph_list'})),
    path('<int:pk>/questionsgraph/start/', views.QuizzModelViewSet.as_view({'get': 'get_questionsgraph_detailed'})),
    path('<int:pk>/questionsgraph/<int:question_id>/', views.QuizzModelViewSet.as_view({'get': 'get_questionsgraph_detailed'})),
    path('quizzecomplexities/', views.QuizzComplexityList.as_view()),
    path('quizzecomplexities/<int:pk>/', views.QuizzComplexityDetail.as_view()),
]
