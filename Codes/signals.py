from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete
from .models import Code, Project, Tag
from .anti_plagiarism.PlagiarismQueue import PlagiarismQueue, PlagiarismQueueEntry

__queue = PlagiarismQueue()

@receiver(pre_save, sender=Code)
def start_plagiarism_checks(sender, instance, **kwargs):
    """
    This function is triggered before a code snippet instance is saved.
    It checks if there are any changes in the source code and if so, it queues it for plagiarism check.

    :param sender: The model class.
    :type sender: django.db.models.Model
    :param instance: The actual instance being saved.
    :type instance: models.Model
    :param kwargs: Keyword arguments
    """
    check_plagiarism: bool = True

    # when updated
    if not instance._state.adding:
        old_instance = Code.objects.get(pk=instance.pk)
        old_value = getattr(old_instance, 'source_code')
        new_value = getattr(instance, 'source_code')
        if old_value == new_value:
            check_plagiarism = False

    if check_plagiarism:
        global __queue
        __queue = PlagiarismQueue()
        __queue.put(PlagiarismQueueEntry(instance.id))

@receiver(post_save, sender=Project)
def select_favorite_project(sender, instance, created, **kwargs):
    """
    This function is triggered after a project instance is saved.
    It checks if the project's owner has a favorite project, if not, it sets the current project as favorite.

    :param sender: The model class.
    :type sender: django.db.models.Model
    :param instance: The actual instance being saved.
    :type instance: models.Model
    :param created: A boolean; True if a new record was created.
    :type created: bool
    :param kwargs: Keyword arguments
    """
    if not created:
        return
    elif instance.owner.profile.favorite_project is not None:
        return

    # if user has no favorite project, set this project as favorite
    instance.owner.profile.favorite_project = instance
    instance.owner.profile.save()

@receiver(post_delete, sender=Project)
def delete_favorite_project(sender, instance, **kwargs):
    """
    This function is triggered after a project instance is deleted.
    If the deleted project was set as favorite, it attempts to set another project as favorite.

    :param sender: The model class.
    :type sender: django.db.models.Model
    :param instance: The actual instance being deleted.
    :type instance: models.Model
    :param kwargs: Keyword arguments
    """
    profile = instance.owner.profile
    if profile.favorite_project is None:
        other_projects = Project.objects.exclude(pk=instance.pk)

        # if possible set other project as favorite
        if other_projects:
            profile.favorite_project = other_projects.first()
            profile.save()

@receiver(post_save, sender=Code)
def update_code_tag(sender, instance, created, **kwargs):
    """
    This function is triggered after a code snippet instance is saved.
    It updates the code tag of the snippet based on its file extension.

    :param sender: The model class.
    :type sender: django.db.models.Model
    :param instance: The actual instance being saved.
    :type instance: models.Model
    :param created: A boolean; True if a new record was created.
    :type created: bool
    :param kwargs: Keyword arguments
    """
    # based of file extension, try to find corresponding tag
    extension = instance.title.split('.')[-1]
    tag = Tag.objects.filter(file_extension=extension).first()
    if instance.code_tag == tag:
        return

    if tag is not None:
        instance.code_tag = tag
        instance.save()
