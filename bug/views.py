from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from bug.models import Bug
# Create your views here.
def bug_manage(request):
    username = request.session.get('user', '')
    bug_list = Bug.objects.all()
    paginator = Paginator(bug_list, 8)
    page = request.GET.get('page',1)
    currentPage = int(page)
    try:
        bug_list = paginator.page(page)
    except PageNotAnInteger:
        bug_list = paginator.page(1)
    except EmptyPage:
        bug_list = paginator.page(paginator.num_pages)
    return render(request, 'bug/bug_manage.html', {"user":username, "bugs": bug_list})

@login_required
def search(request):
    username = request.session.get('user','')
    bugname = request.GET.get("bugname","")
    bugs_list = Bug.objects.filter(bugname__icontains=bugname)
    return render(request,"bug/bug_manage.html",{"user":username,"bugs":bugs_list})