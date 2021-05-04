from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    # user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    birth = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)


class UserInfo(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    school = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    about_me = models.TextField(blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)
