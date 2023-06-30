from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),

    path('account/', views.userAccount, name="account"),
    path('edit_account/', views.editAccount, name="edit_account"),

    path('favourite_tags/', views.favouriteTagsView, name='favourite_tags'),
    path('favourite_tags/<uuid:favourite_tag_id>/', views.favouriteTagsView, name='edit_favourite_tag'),

    path('change_fav_project/<uuid:project_id>/', views.change_favorite_project, name='change_fav_project')
]
