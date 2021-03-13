from django.contrib import admin
from bug.models import Bug

# Register your models here.
class BugAdmin(admin.ModelAdmin):
    list_display = ['bugname','bugdetail','bugstatus','buglevel','bugcreater','bugassign','create_time','id']
    search_fields = ['bugname','bugdetail','id']
    list_filter = ['create_time']
    list_per_page = 10

admin.site.register(Bug)