from django import forms
from .models import Project, Code, Document
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

class ProjectForm(forms.ModelForm):
    """
    This form is used to create and edit Project instances. It uses Django's ModelForm functionality
    to generate fields based on the Project model's fields.

    :param forms.ModelForm: Inherits from Django's ModelForm class.
    :type forms.ModelForm: class
    """
    class Meta:
        """
        Meta class defining the model and fields to be used by the form.
        """
        model = Project
        fields = ['title', 'description']
        labels = {
            'title': 'Tytuł',
            'description': 'Krótki opis',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form. Also, add a custom class 'input' to every field in the form.

        :param args: Variable length argument list.
        :type args: list
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: dict
        """
        super(ProjectForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CodeForm(forms.ModelForm):
    """
    This form is used to create and edit Code instances. It uses Django's ModelForm functionality
    to generate fields based on the Code model's fields.

    :param forms.ModelForm: Inherits from Django's ModelForm class.
    :type forms.ModelForm: class
    """
    class Meta:
        """
        Meta class defining the model and fields to be used by the form.
        """
        model = Code
        fields = ['title', 'description', 'source_code']
        labels = {
            'title': 'Tytuł',
            'description': 'Krótki opis',
            'source_code': 'Kod',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize the form. Also, add a custom class 'input' to every field in the form.

        :param args: Variable length argument list.
        :type args: list
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: dict
        """
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CustomClearableFileInput(ClearableFileInput):
    """
    A custom clearable file input widget. It changes some default texts of the built-in ClearableFileInput.

    :param ClearableFileInput: Inherits from Django's ClearableFileInput class.
    :type ClearableFileInput: class
    """
    initial_text = _('Aktualny plik')
    input_text = _('')
    clear_checkbox_label = _('Usuń')

class DocumentForm(forms.ModelForm):
    """
    This form is used to upload file(s) as Document instances. It uses Django's ModelForm functionality
    to generate a field based on the Document model's 'file' field. It uses a custom widget to allow
    multiple file uploads.

    :param forms.ModelForm: Inherits from Django's ModelForm class.
    :type forms.ModelForm: class
    """
    file = forms.FileField(widget=CustomClearableFileInput(attrs={'multiple': True}), label=_('Plik'))

    class Meta:
        """
        Meta class defining the model and fields to be used by the form.
        """
        model = Document
        fields = ('file', )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form. Also, add a custom 'onchange' attribute to the 'file' field in the form
        which triggers a JavaScript function to display selected files.

        :param args: Variable length argument list.
        :type args: list
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: dict
        """
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'onchange': 'displaySelectedFiles(event)'})