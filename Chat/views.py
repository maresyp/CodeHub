from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import User
# Create your views here.

@login_required(login_url='login')
def lobby(request):
    # TODO: find only users that are matching and sort them based on messages
    page = 'chat'

    context = {'users': User.objects.exclude(id=request.user.id), 'page': page}
    return render(request, 'Chat/lobby.html', context=context)
