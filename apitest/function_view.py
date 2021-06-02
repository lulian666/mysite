from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from apitest.models import Apis


@login_required
@csrf_exempt
def change_api_not_for_test(request):
    is_not_for_test = request.POST.get('is_not_for_test')
    try:
        case_id = request.POST.get('case_id')
        api = Apis.objects.get(id=case_id)
        api.not_for_test = True if is_not_for_test == 'true' else None
        api.save()
        print('status now:', api.not_for_test)
        return HttpResponse('1')
    except:
        return HttpResponse('0')

