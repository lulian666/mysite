from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from account.forms import LoginForm


def user_login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])

            if user:
                login(request, user)
                return HttpResponse('welcome')
            else:
                return HttpResponse('sorry loser')
        else:
            return HttpResponse('pardon?')

    if request.method == 'GET':
        login_form = LoginForm()
        return render(request, "account/login.html", {"form": login_form})



