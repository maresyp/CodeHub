from django.urls import path
from . import views

urlpatterns = [
    path('add_code/', views.addCode, name="add_code"),
    path('edit_code/<uuid:code_id>/', views.editCode, name="edit_code"),
    path('display_code/<uuid:code_id>/', views.displayMyCode, name="display_code"),
    path('delete_code/<uuid:code_id>/', views.deleteCode, name="delete_code"),
]
