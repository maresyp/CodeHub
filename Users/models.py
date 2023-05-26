from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.

class GenderField(models.BooleanField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return 'M' if value else 'K'

    def to_python(self, value):
        if value in (True, False):
            return 'M' if value else 'K'
        return value

    def get_prep_value(self, value):
        return value == 'M'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True, max_length=254, blank=True, null=True) 
    # the maximum length of an email address according to the RFC 5321 specification
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    username = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(125)], default=125)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    profile_image = models.ImageField(upload_to='images/profiles', null=True, 
                                      blank=True, default='images/profiles/user_default.svg')
    gender = GenderField(null=True, blank=True)
    social_github = models.CharField(max_length=2000, null=True, blank=True)
    social_twitter = models.CharField(max_length=2000, null=True, blank=True)
    social_youtube = models.CharField(max_length=2000, null=True, blank=True)
    social_website = models.CharField(max_length=2000, null=True, blank=True)
    social_facebook = models.CharField(max_length=2000, null=True, blank=True)
    favourite_code = models.CharField(max_length=2000, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.username)


class Matches(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fisr_user')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')
    first_status = models.BooleanField()
    second_status = models.BooleanField()

    def __str__(self) -> str:
        return str(self.id)

class Tag(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return str(self.name)

class FavouritesTags(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) 
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self) -> str:
        return str(self.id)
