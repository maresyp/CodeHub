from django.urls import path
from . import views

urlpatterns = [
    path('add_project/', views.addProject, name="add_project"),
    path('edit_project/<uuid:project_id>/', views.editProject, name="edit_project"),
    path('display_project/<uuid:project_id>/', views.displayMyProject, name="display_project"),
    path('delete_project/<uuid:project_id>/', views.deleteProject, name="delete_project"),
    path('display_code/<uuid:code_id>', views.display_code, name="display_code")
]
