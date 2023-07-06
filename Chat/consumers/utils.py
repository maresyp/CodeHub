from Users.models import Matches
from channels.db import database_sync_to_async
from django.db.models import Q


@database_sync_to_async
def is_valid_match(sender, recipient):
    """
    Sync to async function to check if a valid match exists.

    :param sender: The sender's ID.
    :type sender: str
    :param recipient: The recipient's ID.
    :type recipient: str
    :return: A boolean value indicating whether a valid match exists.
    :rtype: bool
    """
    match = Matches.objects.filter(
        (
                Q(first_user=sender, second_user=recipient) |
                Q(first_user=recipient, second_user=sender)
        ) & Q(first_status=True, second_status=True)
    )
    return True if match else False
