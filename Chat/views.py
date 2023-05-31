from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import User, Matches
from .models import Message
from django.db.models import Q
# Create your views here.

@login_required(login_url='login')
def lobby(request):
    matches = Matches.objects.filter(
        Q(first_user=request.user, first_status=True) |
        Q(second_user=request.user, second_status=True)
    )

    friends = User.objects.filter(
        Q(id__in=matches.values_list('first_user', flat=True))
        | Q(id__in=matches.values_list('second_user', flat=True))
    ).exclude(id=request.user.id)

    # TODO: find friend with most recent message and get last 10 messages
    # TODO: find top 10 recent friends ( based on message timestamp ) and get most recent message for each friend

    context = {'friends': friends}
    return render(request, 'Chat/lobby.html', context=context)
