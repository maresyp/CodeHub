from django.urls import path
from . import views

urlpatterns = [
    path('add_project/', views.addProject, name="add_project"),
    path('add_code/<uuid:project_id>/', views.add_code, name="add_code"),
    path('edit_project/<uuid:project_id>/', views.editProject, name="edit_project"),
    path('edit_code/<uuid:code_id>/', views.edit_code, name="edit_code"),
    path('display_project/<uuid:project_id>/', views.displayMyProject, name="display_project"),
    path('delete_project/<uuid:project_id>/', views.deleteProject, name="delete_project"),
    path('delete_code/<uuid:code_id>/', views.delete_code, name="delete_code"),
]
