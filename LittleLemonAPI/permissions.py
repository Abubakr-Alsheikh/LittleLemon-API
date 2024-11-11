from rest_framework import permissions


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="Manager").exists()


class IsManagerOrReadOnly(permissions.BasePermission):
    SAFE_METHODS = ("GET",)  # Allow GET requests by any user type

    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:  # Grant permission for GET
            return True

        return request.user.groups.filter(name="Manager").exists()


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Customer").exists()


class IsDeliveryCrew(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Delivery Crew").exists()


class IsManagerOrDeliveryCrew(permissions.BasePermission):

    def has_permission(self, request, view):
        is_manager = request.user.groups.filter(name="Manager").exists()
        is_delivery_crew = request.user.groups.filter(name="Delivery Crew").exists()

        return is_manager or is_delivery_crew
