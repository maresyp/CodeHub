from .models import Message

def count_unread_messages(request):
    if request.user.is_authenticated:
        unique_senders = set(Message.objects.filter(
            recipient_id=request.user,
            is_read=False
        ).values_list('sender_id', flat=True))
        count = len(unique_senders)
        return {'unread_messages_count': count}
    return {}