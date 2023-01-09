from django.contrib.auth.models import Group
from rest_framework import permissions


def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """

    return user.groups.filter(name=group_name).exists()


class HasAnyGroupPermission(permissions.BasePermission):
    """
    Ensure user is in ANY required groups.
    """

    def has_permission(self, request, view):
        # Get a mapping of methods -> required group.
        required_groups_mapping = getattr(view, 'required_groups', {})

        # Determine the required groups for this particular request method.
        required_groups = required_groups_mapping.get(request.method, [])

        # Return True if the user has all the required groups or is staff.
        return any([
            is_in_group(request.user, group_name) if group_name != '__all__' else True for group_name in required_groups]
        ) or request.user.is_staff
