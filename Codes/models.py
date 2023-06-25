from django.db import models
from Users.models import User
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
import hashlib
from .anti_plagiarism.PlagiarismQueue import PlagiarismQueue, PlagiarismQueueEntry


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
    _source_code_hash = models.CharField(max_length=256, editable=False)
    plagiarism_ratio = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                   null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs) -> None:
        super(Code, self).__init__(*args, **kwargs)
        self._source_code_hash = self._compute_hash()

    def __str__(self) -> str:
        return f"{self.owner} {self.project} {self.title}"

    def _compute_hash(self) -> str:
        return hashlib.sha256(str(self.source_code).encode('utf-8')).hexdigest()

    def save(self, force_insert=False, force_update=False, *args, **kwargs) -> None:
        # if hash of source_code is different from the original one start plagiarism checker
        check_plagiarism: bool = False
        if self._compute_hash() != self._source_code_hash:
            check_plagiarism = True

        super(Code, self).save(force_insert, force_update, *args, **kwargs)
        self._source_code_hash = self._compute_hash()

        if check_plagiarism:
            queue = PlagiarismQueue()
            queue.put(PlagiarismQueueEntry(self.id))


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
