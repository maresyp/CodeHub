from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db.models import OuterRef, Min, F, Count, Q, Subquery
from .models import Profile, FavouritesTags, Tag, Project, Matches
from Codes.models import Code
from .forms import AddFavouriteTagForm, CustomUserCreationForm, ProfileForm, ChangePasswordForm, RemoveFavouriteTagForm


def loginUser(request):
    """
    Login a user.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
    page = 'login'

    if request.user.is_authenticated:
        return redirect('account')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception:
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
    """
    Logout a user.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
    # Get logged in user
    user = request.user

    # Update user status
    Profile.objects.filter(user=user.id).update(is_active=False)

    logout(request)
    messages.info(request, 'Pomyślnie wylogowano!')
    return redirect('login')


def registerUser(request):
    """
    Register a new user.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
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
    """
    Retrieve account details of the logged in user, user's projects and favourite tags.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
    page = 'account'
    user = request.user
    profile = request.user.profile

    # Get tags and values defined by logged in user
    tags = Tag.objects.filter(favouritestags__user_id=user).annotate(
        value=FavouritesTags.objects.filter(tag_id=OuterRef('pk'), user_id=user).values('value')
    ).order_by('-value')

    # Get all projects created by logged in user
    projects = Project.objects.filter(owner=user).order_by('creation_date')

    # Calculate the top 3 tags for each project
    for project in projects:
        top_tags = (Code.objects
                    .filter(project=project)  # filter codes by project
                    .values('code_tag__name')  # group by tag name
                    .annotate(tag_count=Count('code_tag'))  # count number of each tag
                    .order_by('-tag_count'))  # order by count

        # Add the tags as a new attribute to the project
        project.top_tags = list(top_tags[:3])

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
    """
    Enable the logged in user to edit their account details and password.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
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

                # ToDo: System will set default user avatar if user deletes its current

                if profile_form.instance.user and User.objects.exclude(id=profile_form.instance.user.id).filter(
                        email=email).exists():
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


@login_required(login_url='login')
def favouriteTagsView(request):
    """
    View and manage the favourite tags of the logged in user.

    :param request: A Django HttpRequest object.
    :type request: django.http.HttpRequest
    :returns:  A Django HttpResponse object.
    :rtype: django.http.HttpResponse
    """
    user = request.user
    add_form = AddFavouriteTagForm(user=user)
    remove_form = RemoveFavouriteTagForm(user=user)

    if request.method == 'POST':
        if 'add' in request.POST:
            add_form = AddFavouriteTagForm(request.POST, user=request.user)

            if add_form.is_valid():
                tag = add_form.cleaned_data['tag_id']
                if FavouritesTags.objects.filter(user_id=user, tag_id=tag).exists():
                    messages.error(request, 'Ten tag został już dodany.')
                elif FavouritesTags.objects.filter(user_id=user).count() >= 10:
                    messages.error(request, 'Nie możesz dodać więcej niż 10 tagów.')
                else:
                    new_fav_tag = add_form.save(commit=False)
                    new_fav_tag.user_id_id = user.id
                    lowest_value = FavouritesTags.objects.filter(user_id=user).aggregate(Min('value'))['value__min']
                    if lowest_value is not None:
                        new_fav_tag.value = lowest_value - 1
                    else:
                        new_fav_tag.value = 10
                    new_fav_tag.save()
        elif 'remove' in request.POST:
            tag_id = request.POST.get('tag_id')
            tag_to_delete = FavouritesTags.objects.get(user_id=user, id=tag_id)
            FavouritesTags.objects.filter(user_id=user, value__lt=tag_to_delete.value).update(value=F('value') + 1)
            messages.success(request, 'Pomyślnie usunięto tag.')
            tag_to_delete.delete()
        elif 'increase' in request.POST:
            tag_id = request.POST.get('tag_id')
            favourite_tag = FavouritesTags.objects.get(user_id=user, id=tag_id)
            next_favourite_tag = FavouritesTags.objects.filter(user_id=user, value__gt=favourite_tag.value).order_by('value').first()

            if next_favourite_tag:
                favourite_tag.value, next_favourite_tag.value = next_favourite_tag.value, favourite_tag.value
                favourite_tag.save()
                next_favourite_tag.save()
        elif 'decrease' in request.POST:
            tag_id = request.POST.get('tag_id')
            favourite_tag = FavouritesTags.objects.get(user_id=user, id=tag_id)
            previous_favourite_tag = FavouritesTags.objects.filter(user_id=user, value__lt=favourite_tag.value).order_by('-value').first()

            if previous_favourite_tag:
                favourite_tag.value, previous_favourite_tag.value = previous_favourite_tag.value, favourite_tag.value
                favourite_tag.save()
                previous_favourite_tag.save()

    context = {
        'user': user,
        'add_form': add_form,
        'remove_form': remove_form,
        'favourite_tags': FavouritesTags.objects.filter(user_id=user).order_by('-value'),
    }
    return render(request, 'Users/favourite_tags.html', context)

@login_required(login_url='login')
def changeFavoriteProject(request, project_id):
    """
    Change the favorite project of the currently logged-in user.

    Args:
        request (HttpRequest): The request instance.
        project_id (int): The ID of the project to be set as favorite.

    Returns:
        HttpResponseRedirect: Redirect to the 'account' view.

    Raises:
        Http404: The project with provided ID does not exist.
    """
    project = get_object_or_404(Project, id=project_id)
    if project.owner != request.user:
        messages.error(request, 'Nie jesteś właścicielem tego projektu.')
        return redirect('account')

    request.user.profile.favorite_project = project
    request.user.profile.save()

    return redirect('account')

@login_required(login_url='login')
def findBestMatch(request):
    """
    Find the user with the most matching favorite tags compared to the currently logged-in user.

    Args:
        request (HttpRequest): The request instance.

    Returns:
        HttpResponse: Render the 'Users/best_match.html' template.
        HttpResponseRedirect: Redirect to the 'account' view if no other users are available to match.
    """
    # get the current logged in user
    user = request.user

    # get the favourite tags of the logged in user
    user_tags = FavouritesTags.objects.filter(user_id=user)

    # get a list of user ids who are already matched with the logged in user
    matched_users = Matches.objects.filter(Q(first_user=user) | Q(second_user=user)).values_list('first_user', 'second_user')

    # flatten the list of matched users
    matched_user_ids = [item for sublist in matched_users for item in sublist if item != user.id]
    matched_user_ids.append(user.id)

    # create an empty dictionary to store the scores
    scores = {}


    # iterate over all users
    for other_user in User.objects.exclude(id__in=matched_user_ids):
        # get the favourite tags of the other user
        other_user_tags = FavouritesTags.objects.filter(user_id=other_user)

        # calculate the score for the other user
        score = 0
        for user_tag in user_tags:
            for other_tag in other_user_tags:
                if user_tag.tag_id == other_tag.tag_id:
                    score += user_tag.value + other_tag.value

        # store the score for the other user
        scores[other_user.id] = score

    # Check if scores dictionary is not empty
    if scores:
        # find the user with the maximum score
        best_match_user_id = max(scores, key=scores.get)
        best_match_user = User.objects.get(id=best_match_user_id)

        # Get tags and values defined by best match user
        tags = Tag.objects.filter(favouritestags__user_id=best_match_user.id).annotate(
                value=Subquery(FavouritesTags.objects.filter(tag_id=OuterRef('pk'), user_id=best_match_user.id).values('value'))
                ).order_by('-value')


        # Get favorite project of the best match user
        favorite_project_id = getattr(best_match_user.profile.favorite_project, 'id', None)
        if favorite_project_id is not None:
            project = get_object_or_404(Project, id=favorite_project_id)
            codes = Code.objects.filter(Q(project=project)).order_by('-creation_date')
        else:
            project = None
            codes = []

        context = {
            'best_match_user': best_match_user,
            'tags': tags,
            'project': project,
            'codes': codes,
        }
    else:
        messages.error(request, 'Aktualnie nie ma więcej użytkowników, których moglibyśmy do Ciebie dopasować.')
        return redirect('account')

    # return the result
    return render(request, 'Users/best_match.html', context)


@require_POST
@login_required(login_url='login')
def acceptMatch(request, user_id):
    """
    Accept a match by creating a new Match instance with the first_status set to True.

    Args:
        request (HttpRequest): The request instance.
        user_id (int): The ID of the user to be matched with.

    Returns:
        HttpResponseRedirect: Redirect to the 'find_best_match' view.
    """
    # Get the other user
    other_user = User.objects.get(id=user_id)

    # Create a new Match object with first_status=True
    match = Matches(first_user=request.user, second_user=other_user, first_status=True, second_status=None)
    match.save()

    return redirect('find_best_match')

@require_POST
@login_required(login_url='login')
def rejectMatch(request, user_id):
    """
    Reject a match by creating a new Match instance with the first_status set to False.

    Args:
        request (HttpRequest): The request instance.
        user_id (int): The ID of the user to be matched with.

    Returns:
        HttpResponseRedirect: Redirect to the 'find_best_match' view.
    """
    # Get the other user
    other_user = User.objects.get(id=user_id)

    # Create a new Match object with first_status=False
    match = Matches(first_user=request.user, second_user=other_user, first_status=False, second_status=False)
    match.save()

    return redirect('find_best_match')

@login_required(login_url='login')
def getOldestLike(request):
    """
    Get the oldest like received by the currently logged-in user.

    Args:
        request (HttpRequest): The request instance.

    Returns:
        HttpResponse: Render the 'Users/oldest_like.html' template.
        HttpResponseRedirect: Redirect to the 'account' view if there are no likes.
    """
    # pobierz aktualnie zalogowanego użytkownika
    user = request.user

    # szukaj pasujących rekordów, gdzie zalogowany użytkownik jest 'second_user',
    # 'first_status' jest True, a 'second_status' jest None
    matches = Matches.objects.filter(second_user=user, first_status=True, second_status=None)

    # jeśli nie znaleziono żadnego pasującego rekordu, oldest_match będzie None
    if not matches:
        messages.error(request, 'Aktualnie nie masz żadnych polubień swojego profilu.')
        return redirect('account')

    # znajdź najstarszy z pasujących rekordów
    oldest_match = matches.earliest('id')

    # Get tags and values defined by best match user
    tags = Tag.objects.filter(favouritestags__user_id=oldest_match.first_user).annotate(
            value=Subquery(FavouritesTags.objects.filter(tag_id=OuterRef('pk'), user_id=oldest_match.first_user).values('value'))
            ).order_by('-value')

    # Get favorite project of the best match user
    favorite_project_id = getattr(oldest_match.first_user.profile.favorite_project, 'id', None)
    if favorite_project_id is not None:
        project = get_object_or_404(Project, id=favorite_project_id)
        codes = Code.objects.filter(Q(project=project)).order_by('-creation_date')
    else:
        project = None
        codes = []

    context = {
            'matched_user': oldest_match.first_user,
            'tags': tags,
            'project': project,
            'codes': codes,
        }

    return render(request, 'Users/oldest_like.html', context)

@require_POST
@login_required(login_url='login')
def acceptLike(request, user_id):
    """
    Accept a like by setting the second_status of the Match instance to True.

    Args:
        request (HttpRequest): The request instance.
        user_id (int): The ID of the user who liked the currently logged-in user.

    Returns:
        HttpResponseRedirect: Redirect to the 'get_oldest_like' view.

    Raises:
        Http404: The match instance does not exist.
    """
    # Pobierz innego użytkownika
    other_user = get_object_or_404(User, id=user_id)

    # Znajdź obiekt Matches, który spełnia określone kryteria
    match = get_object_or_404(Matches,
                              first_user=other_user,
                              second_user=request.user,
                              first_status=True,
                              second_status=None)

    # Zaktualizuj wartość second_status na True
    match.second_status = True
    match.save()

    return redirect('get_oldest_like')

@require_POST
@login_required(login_url='login')
def rejectLike(request, user_id):
    """
    Reject a like by setting the second_status of the Match instance to False.

    Args:
        request (HttpRequest): The request instance.
        user_id (int): The ID of the user who liked the currently logged-in user.

    Returns:
        HttpResponseRedirect: Redirect to the 'get_oldest_like' view.

    Raises:
        Http404: The match instance does not exist.
    """
    # Pobierz innego użytkownika
    other_user = get_object_or_404(User, id=user_id)

    # Znajdź obiekt Matches, który spełnia określone kryteria
    match = get_object_or_404(Matches,
                              first_user=other_user,
                              second_user=request.user,
                              first_status=True,
                              second_status=None)

    # Zaktualizuj wartość second_status na True
    match.second_status = False
    match.save()

    return redirect('get_oldest_like')
