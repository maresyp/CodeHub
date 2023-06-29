from django import forms
from .models import Project, Code, Document
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description']
        labels = {
            'title': 'Tytuł',
            'description': 'Krótki opis',
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CodeForm(forms.ModelForm):
    class Meta:
        model = Code
        fields = ['title', 'description', 'source_code']
        labels = {
            'title': 'Tytuł',
            'description': 'Krótki opis',
            'source_code': 'Kod',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CustomClearableFileInput(ClearableFileInput):
    initial_text = _('Aktualny plik')
    input_text = _('')
    clear_checkbox_label = _('Usuń')

class DocumentForm(forms.ModelForm):
    file = forms.FileField(widget=CustomClearableFileInput(attrs={'multiple': True}), label=_('Plik'))

    class Meta:
        model = Document
        fields = ('file', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'onchange': 'displaySelectedFiles(event)'})