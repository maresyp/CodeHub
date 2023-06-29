from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Code
from .anti_plagiarism.PlagiarismQueue import PlagiarismQueue, PlagiarismQueueEntry

__queue = PlagiarismQueue()

@receiver(pre_save, sender=Code)
def start_plagiarism_checks(sender, instance, **kwargs):
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
