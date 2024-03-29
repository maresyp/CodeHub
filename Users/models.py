from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.password_validation import validate_password
from django.db import models
from django.contrib.auth.models import User
from Codes.models import Project, Tag
import uuid


# Create your models here.

class Profile(models.Model):
    """
    A class used to represent the Profile model.

    ...

    Attributes:
    user (User): One-to-one relation with User model
    is_active (bool): To indicate whether the user is active
    city (str): The city of the user
    age (int): The age of the user
    bio (str): The bio of the user
    profile_image (ImageField): The profile image of the user
    gender (str): The gender of the user
    social_github (str): The github account link of the user
    social_twitter (str): The twitter account link of the user
    social_youtube (str): The youtube account link of the user
    social_linkedin (str): The linkedin account link of the user
    social_facebook (str): The facebook account link of the user
    favorite_project (Project): The favorite project of the user

    ...

    Methods:
    __str__(): Returns the string representation of the user
    imageURL: Returns the URL of the user's profile image
    """
    GENDER_CHOICES = [
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    city = models.CharField(max_length=50, null=True, blank=True)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(125)], null=True, blank=True)
    bio = models.TextField(max_length=1000, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles', null=True, blank=True, default='profiles/user-default.png')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    social_github = models.CharField(max_length=2000, null=True, blank=True)
    social_twitter = models.CharField(max_length=2000, null=True, blank=True)
    social_youtube = models.CharField(max_length=2000, null=True, blank=True)
    social_linkedin = models.CharField(max_length=2000, null=True, blank=True)
    social_facebook = models.CharField(max_length=2000, null=True, blank=True)
    favorite_project = models.OneToOneField(Project, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.user)

    @property
    def imageURL(self):
        """
        Returns the URL of the user's profile image.

        Returns:
        str: The URL of the profile image
        """
        try:
            url = self.profile_image.url
        except Exception:
            url = ''
        return url

class Matches(models.Model):
    """
    A class used to represent the Matches model.

    ...

    Attributes:
    id (UUIDField): The UUID of the match
    first_user (User): The first user involved in the match
    second_user (User): The second user involved in the match
    first_status (bool): The status of the first user
    second_status (bool): The status of the second user

    ...

    Methods:
    __str__(): Returns the string representation of the match
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    first_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='first_user')
    second_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='second_user')
    first_status = models.BooleanField(null=True, blank=True)
    second_status = models.BooleanField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.first_user) + " + " + str(self.second_user) + " = " + str(self.second_status)


class FavouritesTags(models.Model):
    """
    A class used to represent the FavouritesTags model.

    ...

    Attributes:
    id (UUIDField): The UUID of the favourite tag
    user_id (User): The user to which the tag belongs
    tag_id (Tag): The tag that is marked as favourite
    value (int): The value of the tag

    ...

    Methods:
    __str__(): Returns the string representation of the favourite tag
    """
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self) -> str:
        return str(self.id)
