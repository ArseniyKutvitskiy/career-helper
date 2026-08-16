from django.urls import path
from . import views

urlpatterns = [
    path("questions/", views.create_question),
    path("sessions/<int:session_id>/answer/", views.submit_answer),
    path("history/", views.history),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
]
