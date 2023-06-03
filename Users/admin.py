from django.contrib import admin
from .models import Profile, Matches, FavouritesTags
# Register your models here.

admin.site.register(Profile)
admin.site.register(Matches)
admin.site.register(FavouritesTags)
