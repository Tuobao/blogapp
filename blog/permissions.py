from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # 总是允许请求读取
        # 所以总允许GET, HEAD, OPTIONS请求,
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
