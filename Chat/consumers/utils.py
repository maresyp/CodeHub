from Users.models import Matches
from channels.db import database_sync_to_async
from django.db.models import Q


@database_sync_to_async
def is_valid_match(sender, recipient):
    match = Matches.objects.filter(
        (
                Q(first_user=sender, second_user=recipient) |
                Q(first_user=recipient, second_user=sender)
        ) & Q(first_status=True, second_status=True)
    )
    return True if match else False
