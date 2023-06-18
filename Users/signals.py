from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import Profile, Matches

from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        Profile.objects.create(
            user=user,
        )


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    try:
        instance.user.delete()
    except:
        pass


@receiver(post_save, sender=Matches)
def notify_about_new_match(sender, instance, created, **kwargs):
    pass  # TODO : if user is currently inside chat new match should appear inside friend list

# post_save.connect(createProfile, sender=User)
# post_delete.connect(delete_user, sender=Profile)
