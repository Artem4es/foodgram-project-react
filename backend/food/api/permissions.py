from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
    IsAuthenticatedOrReadOnly,
)


# class AdminOrReadOnly(BasePermission):
#     """
#     Для использования т.к. безопасных методов, пользователь должен быть
#     авторизован и обладать админскими привелегиями в приложении.
#     """

#     def has_permission(self, request, view):
#         return request.method in SAFE_METHODS or (
#             request.user.is_authenticated and request.user.is_admin
#         )

#     def has_object_permission(self, request, view, obj):
#         return request.method in SAFE_METHODS or (
#             request.user.is_authenticated and request.user.is_admin
#         )


class AuthorAdminPermission(IsAuthenticatedOrReadOnly):
    """
    Allows insecure methods only for instance owner or admin.
    Only secure requests otherwise
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )


# class IsSuperUser(BasePermission):
#     """
#     Права доступа пользователя должны быть суперадмин.
#     """

#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.is_superuser


# class IsAdmin(BasePermission):
#     """
#     Права доступа пользователя должны быть админскими.
#     """

#     def has_permission(self, request, view):
#         return request.user.is_authenticated and (request.user.is_admin)
