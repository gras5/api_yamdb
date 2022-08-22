from rest_framework import permissions


class AuthorModAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    request.user == obj.author
                    or request.user.is_moder_role()
                    or request.user.is_admin_role()
                    or request.user.is_superuser
                )
            )
        )


class SuperuserAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS

            or request.user.is_authenticated
            and (
                request.user.is_admin_role()
                or request.user.is_superuser
            )

        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin_role()
                or request.user.is_superuser
            )
        )


class SuperuserOrAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin_role()
                or request.user.is_superuser
            )
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin_role()
                or request.user.is_superuser
            )
        )
