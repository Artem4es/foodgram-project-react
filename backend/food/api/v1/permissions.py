from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class AuthorAdminPermission(IsAuthenticatedOrReadOnly):
    # has_permission определён в IsAuthenticatedOrReadOnly
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
