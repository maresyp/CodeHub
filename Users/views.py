from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import OuterRef
from .models import Profile, FavouritesTags, Tag, Project
from .forms import CustomUserCreationForm, ProfileForm, ChangePasswordForm


# Create your views here.

def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('account')

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

    context = {'page': page}
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

    #Get all codes created by logged in user
    projects = Project.objects.filter(owner=user).order_by('creation_date')

    context = {
        'user': user, 
        'profile': profile, 
        'tags': tags, 
        'projects': projects, 
        'page': page
    }
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    page = 'edit_account'
    user = request.user
    profile = user.profile
    profile_form = ProfileForm(instance=profile)
    password_form = ChangePasswordForm(user)

    if request.method == 'POST':
        if 'profile_save' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                email = profile_form.cleaned_data['email'].lower()

                #ToDo: System will set default user avatar if user deletes its current

                if profile_form.instance.user and User.objects.exclude(id=profile_form.instance.user.id).filter(email=email).exists():
                    profile_form.add_error('email', "Podany adres e-mail jest już w użyciu.")
                else:
                    profile_form.instance.user.email = email
                    profile_form.save()
                    messages.success(request, 'Dane zostały zaktualizowane.')
                    return redirect('edit_account')
        elif 'password_save' in request.POST:
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data.get('new_password1')
                new_password2 = password_form.cleaned_data.get('new_password2')

                if not password_form.user.check_password(old_password):
                    password_form.add_error('old_password', "Podane hasło jest niepoprawne!")
                elif new_password1 and new_password2 and old_password == new_password1:
                    password_form.add_error('new_password1', "Nowe hasło jest takie same jak stare!")
                elif new_password1 and new_password2 and new_password2 != new_password1:
                    password_form.add_error('new_password2', "Hasła nie są takie same!")
                else:
                    password_form.save(commit=True)
                    messages.success(request, 'Hasło zostało zmienione. Zaloguj się ponownie.')
                    return redirect('edit_account')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'page': page,
    }

    return render(request, 'users/user_profile_form.html', context)