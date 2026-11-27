from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class BuildingManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows access only to 'logged in' users from the group Building Managers or superusers"""

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        return user.groups.filter(name="Building Managers").exists()