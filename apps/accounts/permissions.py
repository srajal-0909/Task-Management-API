from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """
    Grants access only to users with the ADMIN role or superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin_role
        )


class IsManagerOrAdminRole(permissions.BasePermission):
    """
    Grants access to users with MANAGER or ADMIN roles.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_admin_role or request.user.is_manager_role)
        )


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing users to edit only their own account, or admins to edit any account.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin_role:
            return True
        return obj.id == request.user.id
