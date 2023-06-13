from django import forms
from .models import Code

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
        super(CodeForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})