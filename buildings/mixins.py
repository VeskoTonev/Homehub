from operator import truediv

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from buildings.models import Apartment, ApartmentMembership

class ApartmentAccessMixin(LoginRequiredMixin, UserPassesTestMixin):

    """
    Allows access to an apartment only if the user is:
    - superuser,
    - manager,
    - user has an active membership for this apartment
    """
    def get_apartment(self):

        if hasattr(self, "get_object"):
            obj = self.get_object()
            if hasattr(obj, "building"):
                return obj
        apartment_id = self.kwargs.get("apartment_pk") or self.kwargs.get("pk")

        return Apartment.objects.filter(pk=apartment_id).select_related("building").first()

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True

        apartment = self.get_apartment()
        if not apartment:
            return False

        if apartment.building.manager_id == user.id:
            return True

        return ApartmentMembership.objects.filter(
            user = user,
            apartment=apartment,
            is_active = True
        ).exists()

