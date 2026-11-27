from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from accounts.models import Profile, User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget = forms.EmailInput(attrs={"placeholder": "name@example.com"}),
        help_text = "Will be used for notifications and identification"
    )

    default_role = forms.CharField(
        label="Base role",
        initial = "Resident",
        disabled=True,
        required=False,
        help_text = "New users begins as Residents"
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name","last_name","password1","password2"]

        def clean_email(self):
            email = self.cleaned_data.get("email","").strip().lower()
            if User.objects.filter(email=email).exists():
                raise ValidationError("User with this email already exists")
            return email

        def save(self, commit=True):
            user = super().save(commit=False)
            user.email = self.cleaned_data["email"]
            if commit:
                user.save()
                Profile.objects.get_or_create(
                    user=user,
                    defaults={"phone_number":"0000000"}
                )
            return user


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150,required=False,label="name")
    last_name = forms.CharField(max_length=150,required=False,label="last name")
    email = forms.CharField(required=True,label="email")

    class Meta:
        model = Profile
        fields = ["phone_number","profile_picture","address"]
        labels = {
            "phone_number":"Phone Number",
            "profile_picture":"Profile Picture",
            "address":"Address"
        }
        widgets = {
            "phone_number":forms.TextInput(attrs={"placeholder":"+359 88 123 4567"}),
            "address":forms.TextInput(attrs={"placeholder":"гр. Варна, ул. Пример 10"})
        }

        def __init__(self,*args,**kwargs):
            self.user = kwargs.pop("user")
            super().__init__(*args,**kwargs)
            if self.user:
                self.fields["first_name"].initial = self.user.first_name
                self.fields["last_name"].initial = self.user.last_name
                self.fields["email"].initial = self.user.email

        def clean_email(self):
            email = self.cleaned_data["email"].strip().lower()
            if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
                raise ValidationError("This email is used by another user.")
            return email

        def save(self, commit=True):
            profile = super().save(commit=False)
            self.user.first_name = self.cleaned_data["first_name"]
            self.user.last_name = self.cleaned_data["last_name"]
            self.user.email= self.cleaned_data["email"]
            if commit:
                self.user.save()
                profile.user = self.user
                profile.save()
            return profile







