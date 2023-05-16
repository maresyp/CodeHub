from django.shortcuts import render
from .models import Profile


# Create your views here.

def profiles(request):
    context = {'profiles': Profile.objects.all()}
    return render(request, 'Users/profiles.html', context=context)


def UserProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    context = {'profile': profile}
    return render(request, 'Users/user-profile.html', context=context)
