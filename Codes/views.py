from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q

from .models import Project, Code, Document
from .forms import ProjectForm, CodeForm, DocumentForm


@login_required(login_url='login')
def addProject(request):
    page = 'add_project'

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')

            if not title:
                form.add_error('title', 'Podaj tytuł dla swojego kodu.')
            elif not description:
                form.add_error('description', 'Dodaj krótki opis o tym czego dotyczy twój kod')
            else:
                new_project = form.save(commit=False)
                new_project.owner = request.user
                new_project.parent = None
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

    if request.user != project.owner:
        messages.error(request, 'Nie jesteś właścicielem tego projektu.')
        return redirect('account')

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')

            if not title:
                form.add_error('title', 'Podaj tytuł dla swojego kodu.')
            elif not description:
                form.add_error('description', 'Dodaj krótki opis o tym czego dotyczy twój kod')
            else:
                form.save()
                messages.success(request, 'Zapisano zmiany.')
    else:
        form = ProjectForm(instance=project)

    context = {
        'page': page,
        'form': form,
        'project': project
    }
    return render(request, 'Projects/add-edit_project.html', context)

@login_required(login_url='login')
def displayMyProject(request, project_id):
    page = 'display_my_project'
    user = request.user

    project = get_object_or_404(Project, id=project_id)
    codes = Code.objects.filter(
        Q(owner=user) & Q(project=project)
    ).order_by('-creation_date')

    context = {
        'page': page,
        'project': project,
        'codes': codes,
        'user': user,
    }
    return render(request, 'Projects/display_project.html', context)

@login_required(login_url='login')
def deleteProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # check if user is owner of project
    if request.user != project.owner:
        messages.error(request, 'Nie jesteś właścicielem tego projektu.')
        return redirect('account')

    project.delete()
    messages.success(request, 'Projekt został usunięty.')
    return redirect('account')

@login_required(login_url='login')
def add_code(request, project_id):
    page = 'add_code'
    project = get_object_or_404(Project, id=project_id)

    if request.user != project.owner:
        messages.error(request, 'Nie jesteś właścicielem tego projektu.')
        return redirect('account')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('file'):
                document = Document(file=file)

                # check if project contains file with the same name
                if Code.objects.filter(Q(owner=request.user) & Q(project=project) & Q(title=document.file.name)).exists():
                    messages.error(request, f'Projekt zawiera już plik o nazwie {document.file.name}.')
                    return redirect('add_code', project_id=project_id)

                try:
                    source_code = document.file.read().decode('utf-8')

                    if len(source_code) > Code.source_code.field.max_length:
                        messages.error(request, f'Plik {document.file.name} jest za duży.')
                        return redirect('add_code', project_id=project_id)

                except Exception:
                    messages.error(request, f'Wystąpił błąd podczas przesyłania {document.file.name}.')
                    return redirect('add_code', project_id=project_id)

                Code.objects.create(
                    owner=request.user,
                    project=project,
                    source_code=source_code,
                    title=document.file.name,
                    description='Brak opisu',
                )

            messages.success(request, 'Pliki zostały przesłane.')
            return redirect('add_code', project_id=project_id)
    else:
        form = DocumentForm()

    context = {
        'page': page,
        'form': form,
        'project': project,
    }

    return render(request, 'Projects/add-edit_code.html', context)

@login_required(login_url='login')
def edit_code(request, code_id):
    page = 'edit_code'
    code = get_object_or_404(Code, id=code_id)

    if request.user != code.project.owner:
        messages.error(request, 'Nie jesteś właścicielem tego kodu.')
        return redirect('account')

    if request.method == 'POST':
        form = CodeForm(request.POST, instance=code)

        if form.is_valid():
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            source_code = form.cleaned_data.get('source_code')

            if not title:
                form.add_error('title', 'Podaj tytuł dla swojego kodu.')
            elif not description:
                form.add_error('description', 'Dodaj krótki opis o tym czego dotyczy twój kod')
            elif not source_code:
                form.add_error('source_code', 'Dodaj kod')
            else:
                form.save()
                messages.success(request, 'Zapisano zmiany.')
        else:
            messages.error(request, 'Wystąpił błąd podczas zapisywania zmian.')
    else:
        form = CodeForm(instance=code)

    context = {
        'page': page,
        'form': form,
        'code': code
    }

    return render(request, 'Projects/add-edit_code.html', context)

@login_required(login_url='login')
def delete_code(request, code_id):
    code = get_object_or_404(Code, id=code_id)
    project = code.project

    if request.user != code.project.owner:
        messages.error(request, 'Nie jesteś właścicielem tego kodu.')
        return redirect('account')

    code.delete()
    messages.success(request, 'Kod został usunięty.')
    return redirect('display_project', project_id=project.id)