from django.db import models

from accounts.models import User
from buildings.models import Apartment


# Create your models here.

class MonthlyFee(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE)
    billing_month = models.DateField()
    amount_due = models.DecimalField(max_digits = 10000, decimal_places = 2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'P', 'pending'
        APPROVED = 'A', 'approved'
        REJECTED = 'R', 'rejected'

    monthly_fee = models.ForeignKey(MonthlyFee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10000, decimal_places=2)
    paid_at = models.DateField()
    payment_method = models.CharField(max_length=20)
    status = models.TextChoices(max_length=20, choices = StatusChoices.choices)
    reference_number = models.CharField(max_length=20)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE)
