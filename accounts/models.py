from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

phone_validator = RegexValidator(regex=r"^\+?[0-9\s()\-]{7,20}$", message = ('Enter a valid phone number'))


class User(AbstractUser):

    email = models.EmailField(max_length=254, unique = True, blank = False, null = False)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE,related_name="profile")
    phone_number = models.CharField(max_length=20, validators = [phone_validator])
    profile_picture = models.ImageField(upload_to = 'profile_pics/', blank = True, null = True)
    address = models.CharField(max_length=100, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"
