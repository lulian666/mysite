from django.contrib import admin

# Register your models here.
from account.models import UserProfile, UserInfo


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birth', 'phone']
    list_filter = ['phone', ]


admin.site.register(UserProfile, UserProfileAdmin)


class UserInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'school', 'company', 'profession', 'address', 'about_me', 'photo']
    list_filter = ['school', 'company', 'profession']


admin.site.register(UserInfo, UserInfoAdmin)
