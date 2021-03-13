from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login


# Create your views here.
from django.urls import reverse

from apitest.models import Apitest, Apistep


def index(request):
    return HttpResponse("Hello, world. You're at the apitest's index.")


def login(request):
    if request.POST:
        username = password = ''
        username = request.POST.get('username')  # 意思是获取html中填写的username
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = username
            # response = HttpResponseRedirect('apitest/home')
            # return response
            return HttpResponseRedirect(reverse('apitest/home'))
        else:
            return render(request, 'apitest/login.html', {'error': 'username or password error'})
    return render(request, 'apitest/login.html')

@login_required
def home(request):
    context = {}
    # context['username'] = 'lulian !'
    context['username'] = request.session.get('user','')
    return render(request, 'apitest/home.html', context)


def test(request):
    return render(request, 'apitest/test.html')

def logout(request):
    return render(request, 'apitest/login.html')

@login_required
def apitest_manage(request):
    apitest_list = Apitest.objects.all()
    username = request.session.get('user','')
    return render(request, "apitest/apitest_manage.html", {"user":username, "apitests": apitest_list})

@login_required
def apistep_manage(request):
    apistep_list = Apistep.objects.all()
    username = request.session.get('user','')
    return render(request, "apitest/apistep_manage.html", {"user":username, "apisteps": apistep_list})