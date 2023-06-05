from django.dispatch.dispatcher import receiver
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import conf
from django.db.models import Case, When, PositiveSmallIntegerField, OuterRef
from .models import Profile, FavouritesTags, Tag
from .forms import CustomUserCreationForm #ProfileForm, SkillForm, MessageForm
#from .utils import searchProfiles, paginateProfiles


# Create your views here.

def loginUser(request):
    page = 'login'
    context = {'page': page}

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Nie istnieje użytkownik o podanej nazwie.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            Profile.objects.filter(user=user.id).update(is_active=True)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')

        else:
            messages.error(request, 'Nazwa użytkownika lub hasło jest niepoprawne.')

    return render(request, 'users/login_register.html', context)


def logoutUser(request):
    # Get logged in user
    user = request.user

    # Update user status
    Profile.objects.filter(user=user.id).update(is_active=False)

    logout(request)
    messages.info(request, 'Pomyślnie wylogowano!')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            email = form.cleaned_data['email'].lower()
            
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()

            # Check if user with the same username or email already exists
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Ten adres email jest już w użyciu.')
            elif User.objects.filter(username=username).exists():
                form.add_error('username', 'Użytkownik o takiej nazwie już istnieje.')
            else:
                user.save()
                messages.success(request, 'Konto użytkownika zostało utworzone!')
                login(request, user)
                return redirect('account')
        else:
            messages.error(
                request, 'Wystąpił problem podczas rejestracji')
            
    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)


@login_required(login_url='login')
def userAccount(request):
    page = 'account'
    user = request.user
    profile = request.user.profile
    
    # Get tags and values defined by logged in user
    tags = Tag.objects.filter(favouritestags__user_id=user).annotate(
        value=FavouritesTags.objects.filter(tag_id=OuterRef('pk'), user_id=user).values('value')
    ).order_by('-value')

    context = {'user': user, 'profile': profile, 'tags': tags, 'page': page}
    return render(request, 'users/account.html', context)