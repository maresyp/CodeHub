from django.contrib import admin
from . models import Project, Code, Tag, CodeTags

# Register your models here.

admin.site.register(Project)
admin.site.register(Code)
admin.site.register(Tag)
admin.site.register(CodeTags)

