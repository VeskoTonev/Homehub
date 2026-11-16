from django.db import models

from accounts.models import User
from buildings.models import Apartment


# Create your models here.

class RepairRequest(models.Model):

    class CategoryChoices(models.TextChoices):
        PLUMBING = "P","plumbing"
        ELECTRICAL = "E","plumbing"
        ELEVATOR = "EL", "elevator"
        FLOOR_CLEANING = "FC", "floo cleaning"
        OTHER = "O", "other"

    class StatusChoices(models.TextChoices):
        PENDING ="P", "pending"
        IN_PROGRESS ="IP", "in progress"
        COMPLETED = "C", "completed"



    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.TextChoices(max_length=20, choices = CategoryChoices.choices)
    priority = models.CharField(max_length=100)
    status = models.TextChoices(max_length=20, choices = StatusChoices.choices)
    image = models.ImageField(upload_to = 'apartments_problems/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)