from django.core.validators import MinValueValidator, MaxValueValidator,MinLengthValidator,RegexValidator
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import User


# Create your models here.

postal_code_validator = RegexValidator(regex=r"^[0-9]{4,10]$", message = "Enter a valid postal code")

class Building(models.Model):
    name = models.CharField(max_length=60, validators = [MinLengthValidator(3)])
    address = models.CharField(max_length=100, validators = [MinLengthValidator(5)])
    city = models.CharField(max_length=50, validators = [MinLengthValidator(3)])
    postal_code = models.CharField(max_length = 10,  validators = [postal_code_validator])
    floors_count = models.PositiveIntegerField(validators =[MinValueValidator(1), MaxValueValidator(50)])
    manager = models.ForeignKey(User, on_delete = models.PROTECT, related_name = "managed_buildings")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition = Q(floors_count__gte = 1),
                name = 'building_minimum_one_floor'
            ),

            models.CheckConstraint(
                condition=Q(floors_count__lte=50),
                name='building_maximum_fifty_floors'
            )
        ]

    def __str__(self):
        return self.name

class Apartment(models.Model):
    building = models.ForeignKey(Building, on_delete = models.PROTECT, related_name ="apartments")
    apartment_number = models.CharField(max_length=10)
    floors = models.PositiveIntegerField(validators =
                                         [MinValueValidator(1), MaxValueValidator(50)])
    area = models.DecimalField(max_digits=10, decimal_places=2,
                               validators =[MinValueValidator(1), MaxValueValidator(10000)])
    rooms_count = models.PositiveIntegerField(validators =[MinValueValidator(1), MaxValueValidator(20)])
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.building_id and self.floors > self.building.floors_count:
            raise ValidationError({
                "floors" : 'Apartment floors cannot exceed building floors.'
            })


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['building', 'apartment_number'],
                name = 'unique_apartment_per_building'
            ),

            models.CheckConstraint(
                condition = Q(area__gte = 1),
                name='apartment_minimum_area'
            ),

            models.CheckConstraint(
                condition=Q(area__lte=10000),
                name='apartment_maximum_area'
            ),

            models.CheckConstraint(
                condition=Q(rooms_count__gte=1),
                name='apartment_minimum_rooms'
            ),

            models.CheckConstraint(
                condition=Q(rooms_count__lte=20),
                name='apartment_maximum_rooms'
            )
        ]

    def __str__(self):
        return f"Apartment {self.apartment_number}"


class ApartmentMembership(models.Model):

    class MembershipRole(models.TextChoices):
        OWNER = "O", "owner"
        TENANT = "T", "tenant"
        FAMILY = "F", "family"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'apartment_memberships')
    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT, related_name = 'memberships')
    membership_role = models.CharField(max_length=1, choices = MembershipRole.choices)
    start_date = models.DateField()
    end_date = models.DateField(blank = True, null = True)
    is_active = models.BooleanField(default=True)

    def clean(self):

        if self.start_date and self.end_date and self.end_date < timezone.localdate() and not self.start_date:
            raise ValidationError({
                'end_date': "End date must be before start date."
            })

        if self.end_date and self.end_date > timezone.localdate() and not self.is_active:
            raise ValidationError({
                'is_active': "Membership cannot be inactive before its end date."
            })

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'apartment'],
                condition= Q(is_active=True),
                name='unique_active_apartment_membership'
            ),

            models.CheckConstraint(
                condition=(Q(end_date__isnull = True) |
                Q(end_date__gte = models.F('start_date'))),
                name='valid_membership_date_range'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.apartment}"




