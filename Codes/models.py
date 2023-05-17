from django.db import models
from Users.models import Profile

# Create your models here.

class Code(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
