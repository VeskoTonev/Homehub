from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from buildings.models import Apartment, ApartmentMembership, Building

class Command(BaseCommand):
    help = "Creates default user groups and assigns model permissions."

    def handle(self, *args, **options):
        residents_group = Group.objects.get_or_create(name="Residents")
        managers_group = Group.objects.get_or_create(name="Building Managers")

        building_ct = ContentType.objects.get_for_model(Building)
        apartment_ct = ContentType.objects.get_for_model(Apartment)
        membership_ct = ContentType.objects.get_for_model(ApartmentMembership)

        manager_perms = Permission.objects.filter(
            content_type__in=[building_ct, apartment_ct, membership_ct]
        )
        managers_group.permissions.set(manager_perms)

        residents_perms = Permission.objects.filter(
            codename__in=["view_building",
                          "view_apartment",
                          "view_apartment_membership"]
        )
        residents_group.permissions.set(residents_perms)

        self.stdout.write(self.style.SUCCESS("Groups and permissions configured."))




