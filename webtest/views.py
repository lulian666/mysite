from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Webcasestep,Webcase
# Create your views here.
@login_required
def webcase_manage(request):
    webcase_list = Webcase.objects.all()
    username = request.session.get('user','')
    return render(request,'webtest/webcase_manage.html', {"user":username, "webcases":webcase_list})

@login_required
def webcasestep_manage(request):
    webcasestep_list = Webcasestep.objects.all()
    username = request.session.get('user','')
    return render(request,'webtest/webcasestep_manage.html', {"user":username, "webcasesteps":webcasestep_list})

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