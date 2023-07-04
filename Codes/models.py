from django.db import models
from Users.models import User
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.

class Project(models.Model):
    """
    The Project class represents a project entity.

    :param models.Model: Django's base model class from which Project inherits.
    :ivar id: Unique identifier for the project.
    :vartype id: models.UUIDField
    :ivar owner: Reference to the User who owns the project.
    :vartype owner: models.ForeignKey
    :ivar title: The project's title.
    :vartype title: models.CharField
    :ivar description: A short description of the project.
    :vartype description: models.CharField
    :ivar creation_date: The date and time the project was created.
    :vartype creation_date: models.DateTimeField
    :ivar last_edit: The date and time the project was last edited.
    :vartype last_edit: models.DateTimeField
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=5000, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.owner} {self.title}"


class Code(models.Model):
    """
    Represents a code snippet entity within a project.

    :ivar id: Unique identifier for the code snippet.
    :vartype id: models.UUIDField
    :ivar owner: Reference to the User who owns the code snippet.
    :vartype owner: models.ForeignKey
    :ivar project: Reference to the Project the code snippet is part of.
    :vartype project: models.ForeignKey
    :ivar title: The code snippet's title.
    :vartype title: models.CharField
    :ivar description: A short description of the code snippet.
    :vartype description: models.CharField
    :ivar source_code: The code snippet's content.
    :vartype source_code: models.TextField
    :ivar code_tag: The tag associated with the code snippet.
    :vartype code_tag: models.ForeignKey
    :ivar plagiarism_ratio: The plagiarism ratio of the code snippet.
    :vartype plagiarism_ratio: models.PositiveIntegerField
    :ivar plagiarized_from: The reference to the original code snippet from which this code was plagiarized.
    :vartype plagiarized_from: models.ForeignKey
    :ivar creation_date: The date and time the code snippet was created.
    :vartype creation_date: models.DateTimeField
    :ivar last_edit: The date and time the code snippet was last edited.
    :vartype last_edit: models.DateTimeField
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=5000, null=True, blank=True)
    source_code = models.TextField(max_length=10000)
    code_tag = models.ForeignKey('Tag', on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    plagiarism_ratio = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=False, blank=True, default=0)
    plagiarized_from = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.owner} {self.project} {self.title}"


class Tag(models.Model):
    """
    Represents a tag entity that can be associated with a code snippet.

    :ivar id: Unique identifier for the tag.
    :vartype id: models.UUIDField
    :ivar title: The tag's title.
    :vartype title: models.CharField
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=50, unique=True)
    file_extension = models.CharField(max_length=10, unique=True)

    def __str__(self) -> str:
        return str(self.name)

class Document(models.Model):
    """
    Model representing a document.

    :ivar file: The file field representing the document file.
    :vartype file: django.db.models.FileField
    """
    file = models.FileField()
