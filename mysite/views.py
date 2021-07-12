from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='/account/login/')
def home(request):
    context = {'username': request.session.get('user', '')}
    return render(request, 'apitest/home.html', context)
