from django.urls import path

from . import views


urlpatterns = [
    path("attempters/", views.AttempterList.as_view(), name="attempter-list"),
    path(
        "attempters/<int:pk>/", views.AttempterDetail.as_view(), name="attempter-detail"
    ),
]
