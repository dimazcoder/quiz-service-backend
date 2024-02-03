from django.urls import path

from . import views


urlpatterns = [
    path('variants/', views.VariantList.as_view()),
    path('variants/<int:pk>/', views.VariantDetail.as_view()),
    path('variantsgraps/', views.VariantsGraphModelViewSet.as_view({'post': 'create_or_update'})),
]
