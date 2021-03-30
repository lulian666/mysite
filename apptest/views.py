from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.shortcuts import render

# Create your views here.
from apptest.models import Appcase, Appcasestep


@login_required
def appcase_manage(request):
    appcase_list = Appcase.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(appcase_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    appcase_count = Appcase.objects.all().count()
    try:
        appcase_list = paginator.page(page)
    except PageNotAnInteger:
        appcase_list = paginator.page(1)
    except EmptyPage:
        appcase_list = paginator.page(paginator.num_pages)
    return render(request,'apptest/appcase_manage.html', {"user":username, "appcases":appcase_list, "appcasecounts": appcase_count})

@login_required
def appcasestep_manage(request):
    appcasestep_list = Appcasestep.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(appcasestep_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    appcasestep_count = Appcasestep.objects.all().count()
    try:
        appcasestep_list = paginator.page(page)
    except PageNotAnInteger:
        appcasestep_list = paginator.page(1)
    except EmptyPage:
        appcasestep_list = paginator.page(paginator.num_pages)
    return render(request,'apptest/appcasestep_manage.html', {"user":username, "appcasesteps":appcasestep_list, "appcasestepcounts": appcasestep_count})

@login_required
def appsearch(request):
    username = request.session.get('user','')
    appcasename = request.GET.get("appcasename","")
    appcase_list = Appcase.objects.filter(appcasename__icontains=appcasename)
    return render(request,"apptest/appcase_manage.html",{"user":username,"appcases":appcase_list})

@login_required
def appstepsearch(request): # tobe continued!!!!!!!!1
    username = request.session.get('user','')
    appcasename = request.GET.get("appcasename","")
    # appcase_list = Appcase.objects.filter(appcasename__icontains=appcasename)
    # appcasestep_list = appcase_list.appcasestep_set.all()
    appcasestep_list = Appcasestep.Appcase.objects.filter(appcasename__icontains=appcasename)

    '''
    print('num:', appcase_list.count())
    appcasestep_list = models.query.QuerySet()
    for appcase in appcase_list:
        # print(appcase.__str__())
        # print(appcase.appcasestep_set.all())
        appcasestep_list.append(appcase.appcasestep_set.all())
    print("1",type(appcase_list))
    for appcasestep in appcasestep_list:
        print(appcasestep.__str__())
    print("2",type(appcasestep_list))
    '''
    return render(request,"apptest/appcasestep_manage.html",{"user":username,"appcasesteps":appcasestep_list})