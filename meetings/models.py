from django.db import models

from accounts.models import User
from buildings.models import Building
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.

class Meeting(models.Model):

    class StatusChoices(models.TextChoices):
        SCHEDULED = 'S', 'scheduled'
        COMPLETED= 'CO', 'completed'
        CANCELED = 'CA', 'canceled'

    building = models.ForeignKey(Building, on_delete = models.PROTECT, related_name='meetings')
    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    location = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    status = models.CharField(max_length=2, choices = StatusChoices.choices,
                              default = StatusChoices.SCHEDULED)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if(
            self.status == self.StatusChoices.SCHEDULED
            and self.scheduled_at
            and self.scheduled_at < timezone.now()
        ):
            raise ValidationError({
                "scheduled_at": 'A scheduled meeting cannot be in the past.'
            })

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['S','CO','CA']),
                name='valid_meeting_status'
            )
        ]

    def __str__(self):
        return self.title

class AgendaItem(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete = models.CASCADE, related_name='agenda_items')
    title = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(100)])
    voting_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ['order']

        constraints = [

            models.CheckConstraint(
                condition=models.Q(order__gte=1),
                name='agenda_order_positive'
            ),

            models.CheckConstraint(
                condition=models.Q(order__lte=100),
                name='agenda_order_maximum'
            )
        ]

    def __str__(self):
        return f"{self.order} - {self.title}"


class Vote(models.Model):

    class VoteChoices(models.TextChoices):
        YES = 'Y', 'Yes'
        NO = 'N', 'No'
        ABSTAIN = 'A', 'Abstain'

    agenda_item = models.ForeignKey(AgendaItem, on_delete = models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    choice = models.CharField(max_length=1, choices = VoteChoices.choices)
    voted_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.agenda_item_id and not self.agenda_item.voting_enabled:
            raise ValidationError({
                "agenda_item": 'Voting is disabled for this agenda item.'
            })

        if self.agenda_item_id and self.user_id:

            meeting = self.agenda_item.meeting

            is_participating = MeetingParticipants.objects.filter(
                meeting=meeting,
                user=self.user
            ).exists()

            if not is_participating:
                raise ValidationError({
                    "user": 'The user is not a participant in this meeting.'
                })


    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=['agenda_item', 'user'],
                name='unique_vote_per_agenda_item_user'
            ),

            models.CheckConstraint(
                condition=models.Q(choice__in=['Y','N','A']),
                name='agenda_vote_choice'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.choice}"


class MeetingParticipants(models.Model):

    class AttendanceStatus(models.TextChoices):
        INVITED = 'I', 'Invited'
        ACCEPTED = 'AC', 'Accepted'
        ATTENDED = 'AT', 'Attended'
        ABSENT = 'AB', 'Absent'

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE,related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='meeting_participants')
    attendance_status = models.CharField(max_length=20, choices = AttendanceStatus.choices,default=AttendanceStatus.INVITED)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=['meeting', 'user'],
                name='unique_meeting_participant'
            ),

            models.CheckConstraint(
                condition=models.Q(attendance_status__in=['I','AC','AT','AB']),
                name='valid_attendance_status'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.meeting.title}"






