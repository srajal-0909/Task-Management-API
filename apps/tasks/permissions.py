from rest_framework import permissions


class IsTaskOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing:
    - Admin: Full access (read, write, delete).
    - Manager: Full access or elevated view/edit.
    - Member: Can read if owner or assigned; can modify/delete only if owner.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Admin has unrestricted access
        if request.user.is_admin_role:
            return True

        # Read-only permissions for safe methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_manager_role:
                return True
            return obj.owner_id == request.user.id or obj.assigned_to_id == request.user.id

        # Update / Patch / Action execution permissions (POST, PUT, PATCH)
        if request.method in ('PUT', 'PATCH', 'POST'):
            if request.user.is_manager_role:
                return True
            # Allow assigned member or owner to update/complete task
            if obj.assigned_to_id == request.user.id or obj.owner_id == request.user.id:
                return True
            return False

        # Delete permission strictly reserved for Owner or Admin
        if request.method == 'DELETE':
            return obj.owner_id == request.user.id or request.user.is_admin_role

        return False


class IsCategoryOwnerOrAdmin(permissions.BasePermission):
    """
    Ensures users can only manage their own categories unless they are admins.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin_role:
            return True
        return obj.owner_id == request.user.id
