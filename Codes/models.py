from django.db import models
from Users.models import User
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Project(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=5000, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.owner} {self.title}"


class Code(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=5000, null=True, blank=True)
    source_code = models.TextField(max_length=10000)
    plagiarism_ratio = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=False, blank=True, default=0)
    plagiarized_from = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.owner} {self.project} {self.title}"


class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return str(self.name)


class CodeTags(models.Model):
    code_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.code_id)

class Document(models.Model):
    file = models.FileField()
