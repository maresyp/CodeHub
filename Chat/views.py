from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import User, Matches
from .models import Message
from django.db.models import Q
from django.utils import timezone
from datetime import datetime


# Create your views here.

@login_required(login_url='login')
def lobby(request):
    AMOUNT_OF_FRIENDS = 10  # TODO: maybe change ?
    page = 'chat'
    matches = Matches.objects.filter(
        Q(first_user=request.user, first_status=True) |
        Q(second_user=request.user, second_status=True)
    )

    friends = list(User.objects.filter(
        Q(id__in=matches.values_list('first_user', flat=True))
        | Q(id__in=matches.values_list('second_user', flat=True))
    ).exclude(id=request.user.id))

    # find one message for every friend
    for friend in friends:
        message = Message.objects.filter(
            Q(sender_id=request.user, recipient_id=friend) |
            Q(sender_id=friend, recipient_id=request.user)
        ).order_by('-send_timestamp').first()
        friend.last_message = message

    # sort friends based on the last message timestamp
    friends = sorted(
        friends,
        key=lambda f: getattr(f.last_message, 'send_timestamp', timezone.make_aware(datetime.min)),
        reverse=True
    )

    # get 10 recent messages from friend with most recent message
    recent_friend = friends[0] if friends else None  # get the first friend
    if recent_friend:
        last_10_messages = Message.objects.filter(
            Q(sender_id=request.user, recipient_id=recent_friend) |
            Q(sender_id=recent_friend, recipient_id=request.user)
        ).order_by('-send_timestamp')[:10]

        recent_friend.messages = reversed(last_10_messages)

    context = {
        'friends': friends[:AMOUNT_OF_FRIENDS],
        'page': page
    }
    return render(request, 'Chat/lobby.html', context=context)
