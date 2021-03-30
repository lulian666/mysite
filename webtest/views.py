from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from .models import Webcasestep,Webcase
# Create your views here.
@login_required
def webcase_manage(request):
    webcase_list = Webcase.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(webcase_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    webcase_count = Webcase.objects.all().count()
    try:
        webcase_list = paginator.page(page)
    except PageNotAnInteger:
        webcase_list = paginator.page(1)
    except EmptyPage:
        webcase_list = paginator.page(paginator.num_pages)
    return render(request,'webtest/webcase_manage.html', {"user":username, "webcases":webcase_list, "webcasecounts": webcase_count})

@login_required
def webcasestep_manage(request):
    webcasestep_list = Webcasestep.objects.all()
    username = request.session.get('user','')
    paginator = Paginator(webcasestep_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    webcasestep_count = Webcasestep.objects.all().count()
    try:
        webcasestep_list = paginator.page(page)
    except PageNotAnInteger:
        webcasestep_list = paginator.page(1)
    except EmptyPage:
        webcasestep_list = paginator.page(paginator.num_pages)
    return render(request,'webtest/webcasestep_manage.html', {"user":username, "webcasesteps":webcasestep_list, "webcasestepcounts": webcasestep_count})

@login_required
def websearch(request):
    username = request.session.get('user','')
    webcasename = request.GET.get("webcasename","")
    webcase_list = Webcase.objects.filter(webcasename__icontains=webcasename)
    return render(request,"webtest/webcase_manage.html",{"user":username,"webcases":webcase_list})

@login_required
def webstepsearch(request):
    username = request.session.get('user','')
    webcasename = request.GET.get("webcasename","")
    webcasestep_list = Webcasestep.objects.filter(webcasename__icontains=webcasename)
    return render(request,"webtest/webcasestep_manage.html",{"user":username,"webcasesteps":webcasestep_list})