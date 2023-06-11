from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import User
from Codes.models import Code, Tag
import uuid


# Create your models here.

class GenderField(models.BooleanField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return 'Mężczyzna' if value else 'Kobieta'

    def to_python(self, value):
        if value in (True, False):
            return 'Mężczyzna' if value else 'Kobieta'
        return value

    def get_prep_value(self, value):
        return value == 'Mężczyzna'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    city = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(125)], null=True, blank=True)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles', null=True, 
                                      blank=True, default='profiles/user-default.png')
    gender = GenderField(null=True, blank=True)
    social_github = models.CharField(max_length=2000, null=True, blank=True)
    social_twitter = models.CharField(max_length=2000, null=True, blank=True)
    social_youtube = models.CharField(max_length=2000, null=True, blank=True)
    social_linkedin = models.CharField(max_length=2000, null=True, blank=True)
    social_facebook = models.CharField(max_length=2000, null=True, blank=True)
    favourite_code = models.ForeignKey(Code, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)
    
    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''
        return url

class Matches(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')
    first_status = models.BooleanField()
    second_status = models.BooleanField()

    def __str__(self) -> str:
        return str(self.first_user) + " + " + str(self.second_user) + " = " + str(self.second_status)


class FavouritesTags(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE) 
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self) -> str:
        return str(self.id)
