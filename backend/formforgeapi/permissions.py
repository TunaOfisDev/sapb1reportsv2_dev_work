# backend/formforgeapi/permissions.py
from rest_framework import permissions

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow creators of an object to edit it.
    Assumes the model instance has a `created_by` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the submission.
        # obj burada FormSubmission instance'ı olacak.
        return obj.created_by == request.user