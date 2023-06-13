from django.urls import path
from . import views

urlpatterns = [
    path('add_code/', views.addCode, name="add_code"),
]
