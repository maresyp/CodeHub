from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from .models import Project
from .forms import ProjectForm


@login_required(login_url='login')
def addProject(request):
    page = 'add_project'

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            source_code = form.cleaned_data.get('source_code')

            if not title:
                form.add_error('title', 'Podaj tytuł dla swojego kodu.')
            elif not description:
                form.add_error('description', 'Dodaj krótki opis o tym czego dotyczy twój kod')
            elif not source_code:
                form.add_error('source_code', 'Kolego, nie można dodać kodu bez kodu.')
            else:
                new_project = form.save(commit=False)
                new_project.owner = request.user
                new_project.plagiarism_ratio = 0
                new_project.save()

                messages.success(request, 'Projekt został poprawnie utworzony.')
                return redirect('account')
    else:
        form = ProjectForm()

    context = {
        'page': page,
        'form': form
    }
    return render(request, 'Projects/add-edit_project.html', context)


@login_required(login_url='login')
def editProject(request, project_id):
    page = 'edit_project'
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            source_code = form.cleaned_data.get('source_code')

            if not title:
                form.add_error('title', 'Podaj tytuł dla swojego kodu.')
            elif not description:
                form.add_error('description', 'Dodaj krótki opis o tym czego dotyczy twój kod')
            elif not source_code:
                form.add_error('source_code', 'Kolego, nie można dodać kodu bez kodu.')
            else:
                form.save()
                messages.success(request, 'Zapisano zmiany.')
    else:
        form = ProjectForm(instance=project)

    context = {
        'page': page,
        'form': form
    }
    return render(request, 'Projects/add-edit_project.html', context)

@login_required(login_url='login')
def displayMyProject(request, project_id):
    page = 'display_my_project'
    user = request.user

    project = get_object_or_404(Project, id=project_id)

    context = {
        'page': page,
        'project': project,
        'user': user, 
    }
    return render(request, 'Projects/display_project.html', context)

@login_required(login_url='login')
def deleteProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    project.delete()
    messages.success(request, 'Projekt został usunięty.')
    return redirect('account')

