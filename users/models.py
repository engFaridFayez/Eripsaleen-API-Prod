import os

from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

ROLES = [
    ('admin','admin'),
    ('assistant','assistant'),
    ('user','user'),
]


def upload_path(instance,filename):
    return os.path.join('images','avatars',str(instance.username),filename)
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    joined_date = models.DateField(null=True,blank=True)
    birth_date = models.DateField(null=True,blank=True)
    role = models.CharField(max_length=50,choices=ROLES,default="user")
    image = models.ImageField(upload_to=upload_path,blank=True,null=True)

