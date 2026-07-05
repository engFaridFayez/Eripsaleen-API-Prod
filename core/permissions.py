from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAdmin(BasePermission):
    """
    يسمح بالقراءة لأي شخص،
    ويمنع الإنشاء أو التعديل أو الحذف إلا للمستخدمين الـ Staff.
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True

        # POST, PUT, PATCH, DELETE
        return (
            request.user.is_authenticated
            and request.user.is_staff
        )