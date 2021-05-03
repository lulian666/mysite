

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


# class RegisterForm(forms.ModelForm):
#     password = forms.CharField()
#     password2 = forms.CharField()
#
#     class Meta:
#         model = Profile
#         fields = ['username', 'email']