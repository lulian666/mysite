from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from account.models import UserProfile, UserInfo


@login_required(login_url='/account/login/')
def home(request):
    context = {'username': request.session.get('user', '')}
    return render(request, 'home.html', context)


def left(request):
    return render(request, "left.html")


@login_required(login_url='/account/login/')
def my_information(request):
    user = User.objects.get(username=request.user.username)
    userprofile = UserProfile.objects.filter(user=user)
    userinfo = UserInfo.objects.filter(user=user)
    return render(request, 'account/myself.html', {"user": user, "userprofile": userprofile, "userinfo": userinfo})
