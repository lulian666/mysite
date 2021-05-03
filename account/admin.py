from django.contrib import admin

# Register your models here.
from account.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth', 'phone']
    list_filter = ['phone', ]


admin.site.register(UserProfile, UserProfileAdmin)
