from django.db import models

from accounts.models import User
from buildings.models import Apartment, ApartmentMembership
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError


# Create your models here.

class RepairRequest(models.Model):

    class CategoryChoices(models.TextChoices):
        PLUMBING = "P","Plumbing"
        ELECTRICAL = "E","Electrical"
        ELEVATOR = "EL", "Elevator"
        FLOOR_CLEANING = "FC", "Floor Cleaning"
        OTHER = "O", "Other"

    class StatusChoices(models.TextChoices):
        PENDING ="P", "Pending"
        IN_PROGRESS ="IP", "In Progress"
        COMPLETED = "C", "Completed"

    class PriorityChoices(models.TextChoices):
        LOW ="L", "Low"
        MEDIUM ="M", "Medium"
        HIGH = "H", "High"
        URGENT = "U", "Urgent"




    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT,related_name='repair_requests')
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT,related_name='repair_requests')
    title = models.CharField(max_length=100, validators=[MinLengthValidator(5),MaxLengthValidator(100)])
    description = models.TextField(validators=[MinLengthValidator(5)])
    category = models.TextChoices(max_length=20, choices = CategoryChoices.choices)
    priority = models.CharField(max_length=20, choices=PriorityChoices.choices)
    status = models.TextChoices(max_length=20, choices = StatusChoices.choices)
    image = models.ImageField(upload_to = 'apartments_problems/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.apartment_id and self.submited_by_id:

            is_member = ApartmentMembership.objects.filter(
                user = self.submitted_by,
                apartment=self.apartment,
                is_active=True
            ).exists()

            if not is_member:
                raise ValidationError({
                    'submitted_by' : 'You must be an active apartment memeber to submit a repair request.'
                })


    class Meta:
        constraints = [

            models.CheckConstraint(
                condition=models.Q(category__in=['P', 'E', 'El','FC','O']),
                name='valid_repair_category'
            ),

            models.CheckConstraint(
                condition=models.Q(status__in=['P', 'IP', 'C']),
                name='valid_repair_status'
            ),

            models.CheckConstraint(
                condition=models.Q(priority__in=['L', 'M', 'H', 'U']),
                name='valid_repair_priority'
            )

        ]

        def __str__(self):
            return self.title
