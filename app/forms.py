from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import AuthenticationForm

class ProfileForm(forms.ModelForm):
    cni = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'class': 'form-input'}))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(max_length=150, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))



    class Meta:
        model = Profile
        fields = ['cni', 'first_name', 'last_name', 'email', 'password']

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        profile.user = user
        if commit:
            profile.save()
        return profile
    
  

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Mail", max_length=30,
                               widget=forms.TextInput(attrs={'placeholder': 'exemple@gmail.Com'}))
    password = forms.CharField(label="Mot de passe", max_length=30,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))

