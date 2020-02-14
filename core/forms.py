from django import forms
from django.contrib.auth import authenticate, get_user_model
from .models import Document

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(label="Username",max_length = 25, widget=forms.TextInput(attrs={
        'class':"form-control", 'placeholder':'Enter Username'
    }))
    password = forms.CharField(label="Password",widget=forms.PasswordInput(attrs={
        'class':"form-control", 'placeholder':'Enter Password'
    }), max_length = 15)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username = username, password = password)
            if not user:
                raise forms.ValidationError("this user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Invalid Credentials")
            if not user.is_active:
                raise forms.ValidationError("this user not active")
        return super(UserLoginForm, self).clean(*args, **kwargs)

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label = 'Email Address',widget = forms.EmailInput(attrs={'class':"form-control", 'placeholder':'Enter Email' }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control", 'placeholder':'Enter Password' }), label  = 'password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control", 'placeholder':'ReEnter Password' }), label  = 'Re-password')
    secret_key = forms.CharField(max_length = 25,widget=forms.TextInput(attrs={
        'class':"form-control", 'placeholder':'Enter SecretKey'
    }))

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2'
        ]
        widgets ={
            'username' : forms.TextInput(attrs={'class':"form-control", 'placeholder':'Enter Username' })
        }
        

    def clean(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        email = self.cleaned_data.get('email')
        print(password,"asdasda", password2)
        if password != password2:
            raise forms.ValidationError("password must Match")
        email_qs = User.objects.filter(email = email)
        if email_qs.exists():
            raise forms.ValidationError(
            'this email is already used'
        )
        return super(UserRegistrationForm, self).clean()

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields  = [
            'document'
        ]
        widgets = {
            'document' : forms.FileInput(attrs={
                'class':"custom-file-input"
            })
        }

