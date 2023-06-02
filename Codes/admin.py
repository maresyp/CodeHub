from django.contrib import admin
from . models import Code, Tag, CodeTags

# Register your models here.

admin.site.register(Code)
admin.site.register(Tag)
admin.site.register(CodeTags)

