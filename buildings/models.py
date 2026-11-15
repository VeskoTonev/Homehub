from django.db import models

from accounts.models import User


# Create your models here.

class Building(models.Model):
    name = models.CharField(max_length=60)
    address = models.CharField(max_length=60)
    city = models.CharField(max_length=40)
    postal_code = models.CharField(max_length = 30)
    floors_count = models.PositiveIntegerField()
    manager = models.ForeignKey(User, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete = models.CASCADE)
    apartment_number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)
    rooms_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ApartmentMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    membership_role = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)