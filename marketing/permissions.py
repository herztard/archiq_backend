# banners/permissions.py
from rest_framework import permissions

class AllowAnyListGet(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET' and view.action == 'list':
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return user.is_staff or user.groups.filter(name='Managers').exists()

class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_staff or user.groups.filter(name='Managers').exists()
