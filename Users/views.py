from django.shortcuts import render
from .models import Profile
from .models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.

def login_user(request):
    page = 'login'

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profiles')
        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'Users/login_register.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'User was logged out')
    return redirect('login')


def register_user(request):
    page = 'register'
    context: dict = {'page': page}
    return render(request, 'Users/login_register.html', context=context)


def profiles(request):
    context = {'profiles': Profile.objects.all()}
    return render(request, 'Users/profiles.html', context=context)


def UserProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    context = {'profile': profile}
    return render(request, 'Users/user-profile.html', context=context)
