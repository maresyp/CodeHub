from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime
from .forms import CodeForm

@login_required(login_url='login')
def addCode(request):
    page = 'add_code'

    if request.method == 'POST':
        form = CodeForm(request.POST)
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
                new_code = form.save(commit=False)
                new_code.owner = request.user
                new_code.plagiarism_ratio = 0
                new_code.save()

                messages.success(request, 'Kod został poprawnie utworzony.')
                return redirect('account')
    else:
        form = CodeForm()

    context = {
        'page': page,
        'form': form
    }
    return render(request, 'Codes/add_code.html', context)
