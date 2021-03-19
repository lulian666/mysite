from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from bug.models import Bug
# Create your views here.
def bug_manage(request):
    username = request.session.get('user', '')
    bug_list = Bug.objects.all()
    return render(request, 'bug/bug_manage.html', {"user":username, "bugs": bug_list})

@login_required
def search(request):
    username = request.session.get('user','')
    bugname = request.GET.get("bugname","")
    bugs_list = Bug.objects.filter(bugname__icontains=bugname)
    return render(request,"bug/bug_manage.html",{"user":username,"bugs":bugs_list})