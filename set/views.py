from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.shortcuts import render
from set.models import Set
# Create your views here.

def set_manage(request):
    username = request.session.get('user', '')
    set_list = Set.objects.all()
    paginator = Paginator(set_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    try:
        set_list = paginator.page(page)
    except PageNotAnInteger:
        set_list = paginator.page(1)
    except EmptyPage:
        set_list = paginator.page(paginator.num_pages)
    return render(request, 'set/set_manage.html', {"user":username, "sets": set_list})

def set_user(request):
    username = request.session.get('user', '')
    user_list = User.objects.all()
    return render(request, 'set/set_user.html', {"user":username, "users": user_list})

@login_required
def search(request):
    username = request.session.get('user','')
    search_setname = request.GET.get("setname","")
    set_list = Set.objects.filter(setname__icontains=search_setname)
    return render(request,"set/set_manage.html",{"user":username,"sets":set_list})

@login_required
def usersearch(request):
    username = request.session.get('user','')
    searchusername = request.GET.get("username","")
    user_list = User.objects.filter(username__icontains=searchusername)
    return render(request,"set/set_user.html",{"user":username,"users":user_list})