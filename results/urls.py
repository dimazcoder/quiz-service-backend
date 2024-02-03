from django.urls import path

from . import views


urlpatterns = [
    path('', views.ResultModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('<int:pk>/', views.ResultModelViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})),
]
