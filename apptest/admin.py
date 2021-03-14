from django.contrib import admin
from .models import Appcase,Appcasestep
# Register your models here.
class AppcasestepAdmin(admin.TabularInline):
    list_display = ['appteststep','apptestobjname','appfindmethod','appevelement','appoptmethod','appassertdata','apptestresult','create_time','id','appcase']
    model = Appcasestep
    extra = 1


class AppcaseAdmin(admin.ModelAdmin):
    list_display = ['appcasename','apptestresult','create_time','id']
    inlines = [AppcasestepAdmin]
    search_fields = ['appcasename','apptestresult']
    list_filter = ['create_time']
    list_per_page = 10

admin.site.register(Appcase, AppcaseAdmin)