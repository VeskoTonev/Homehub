from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from accounts.models import User
from buildings.models import Apartment


# Create your models here.

class MonthlyFee(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.PROTECT, related_name = 'monthly_fees')
    billing_month = models.DateField()
    amount_due = models.DecimalField(max_digits = 10, decimal_places = 2, validators = [MinValueValidator(0.01)])
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):

        if self.billing_month and self.due_date:
            if self.due_date < self.billing_month:
                raise ValidationError({
                    'due_date':"Due date cannot be before billing month"
                })

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['apartment', 'billing_month'],
                name = 'unique_monthly_fee_per_apartment'
            ),

            models.CheckConstraint(
                condition = models.Q(amount_due__gt = Decimal("0.01")),
                name='unique_monthly_fee_amount_positive'
            ),
        ]

    def __str__(self):
        return f"{self.apartment} - {self.billing_month}"



class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'P', 'pending'
        APPROVED = 'A', 'approved'
        REJECTED = 'R', 'rejected'

    class PaymentMethodChoices(models.TextChoices):
        CASH = 'C', 'cash'
        BANK = 'B', 'bank'
        CARD = 'CA', 'card'

    monthly_fee = models.ForeignKey(MonthlyFee, on_delete=models.PROTECT, related_name = 'payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators = [MinValueValidator(0.01)])
    paid_at = models.DateField()
    payment_method = models.CharField(max_length=2, choices = PaymentMethodChoices.choices)
    status = models.CharField(max_length=1, choices = StatusChoices.choices, default = StatusChoices.PENDING)
    reference_number = models.CharField(max_length=20, blank = True, null = True, unique= True)
    recorded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name = 'recorded_payments')

    def clean(self):
        if self.status == self.StatusChoices.APPROVED and not self.paid_at:
            raise ValidationError({
                'paid_at': "Approved payments must have a payment date."
            })

        if self.monthly_fee_id and self.amount is not None:
            if self.amount > self.monthly_fee.amount_due:
                raise ValidationError({
                    'amount': "Payment cannot exceed the monthly fee amount."
                })

    class Meta:

        constraints = [

            models.CheckConstraint(
                condition=models.Q(amount__gt = 0),
                name='payment_amount_positive'
            ),

            models.CheckConstraint(
                condition=models.Q(status__in=['P', 'A', 'R']),
                name='valid_payment_status'
            )
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
