from django.urls import path

from . import views


urlpatterns = [
    path('', views.UserModelViewSet.as_view({'post': 'create'})),
    path('<int:pk>/', views.UserModelViewSet.as_view({'get': 'retrieve'})),
]
