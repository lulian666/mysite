from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate, login


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the apptest's index.")

def login(request):
    if request.POST:
        username = password = ''
        username = request.POST.get('username') #意思是获取html中填写的username
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            request.session['user'] = username
            response = HttpResponseRedirect('/home/')
            return response
        else:
            return render(request, 'login.html', {'error': 'username or password error'})

    return render(request,'login.html')

def home(request):
    context = {}
    context['username'] = 'lulian !'
    return render(request, 'home.html', context)

def test(request):
    return render(request,'test.html')