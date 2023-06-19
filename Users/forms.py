from django.forms import CharField, Form, ModelChoiceField, ModelForm, EmailField, PasswordInput, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, FavouritesTags, Tag


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'email', 
            'username', 
            'password1', 
            'password2']
        labels = {
            'first_name': 'Imię',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class ProfileForm(ModelForm):
    email = EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['city', 'age', 'bio', 'profile_image', 'gender',
                  'social_github', 'social_twitter', 'social_youtube',
                  'social_linkedin', 'social_facebook']
        labels = {
            'city': 'Lokalizacja',
            'age': 'Wiek',
            'bio': 'O mnie',
            'profile_image': 'Zdjęcie profilowe',
            'gender': 'Płeć',
            'social_github': 'GitHub', 
            'social_twitter': 'Twitter', 
            'social_youtube': 'Youtube',
            'social_linkedin': 'LinkedIn', 
            'social_facebook': 'Facebook',
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        profile.user.email = self.cleaned_data['email'].lower()
        if commit:
            profile.save()
            profile.user.save()
        return profile


class ChangePasswordForm(Form):
    old_password = CharField(
        label="Aktualne hasło",
        widget=PasswordInput(attrs={'autocomplete': 'current-password'}))

    new_password1 = CharField(
        label="Nowe hasło",
        widget=PasswordInput(attrs={'autocomplete': 'new-password'}),
        validators=[validate_password]
    )
    new_password2 = CharField(
        label="Potwierdź nowe hasło",
        widget=PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
    

class AddFavouriteTagForm(ModelForm):
    class Meta:
        model = FavouritesTags
        fields = ['tag_id']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddFavouriteTagForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['tag_id'].queryset = Tag.objects.exclude(favouritestags__user_id=self.user)

    def clean_tag_id(self):
        tag_id = self.cleaned_data['tag_id']
        if FavouritesTags.objects.filter(user_id=self.user, tag_id=tag_id).count() >= 10:
            raise ValidationError("Nie możesz dodać więcej niż 10 tagów.")
        return tag_id


class RemoveFavouriteTagForm(Form):
    tag_id = ModelChoiceField(queryset=Tag.objects.all())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['tag_id'].queryset = Tag.objects.filter(favouritestags__user_id=self.user)

    def clean_tag_id(self):
        tag_id = self.cleaned_data.get('tag_id')

        if not FavouritesTags.objects.filter(user_id=self.user, tag_id=tag_id).exists():
            raise ValidationError("Ten tag nie jest dodany.")
        return tag_id


