from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import User, Matches
from .models import Message
from django.db.models import Q, Max
# Create your views here.

@login_required(login_url='login')
def lobby(request):
    AMOUNT_OF_FRIENDS = 10
    matches = Matches.objects.filter(
        Q(first_user=request.user, first_status=True) |
        Q(second_user=request.user, second_status=True)
    )

    friends = User.objects.filter(
        Q(id__in=matches.values_list('first_user', flat=True))
        | Q(id__in=matches.values_list('second_user', flat=True))
    ).exclude(id=request.user.id)

    # find one message for every friend
    messages = {}
    friend_timestamps = {}
    for friend in friends:
        message = Message.objects.filter(
            Q(sender_id=request.user, recipient_id=friend) |
            Q(sender_id=friend, recipient_id=request.user)
        ).order_by('-send_timestamp').first()
        messages[friend.username] = message
        friend_timestamps[friend] = message.send_timestamp if message else None

    # sort friends based on the last message timestamp
    friends = sorted(friend_timestamps, key=friend_timestamps.get, reverse=True)

    print(friends)
    # TODO: find friend with most recent message and get last 10 messages

    context = {
        'friends': friends[:AMOUNT_OF_FRIENDS],
        'top_messages': messages
    }
    return render(request, 'Chat/lobby.html', context=context)
