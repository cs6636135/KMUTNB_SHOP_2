from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator to restrict view access to specific roles ('admin', 'staff').
    Redirects to login if unauthenticated, or raises PermissionDenied / redirects if unauthorized.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'กรุณาเข้าสู่ระบบก่อนเข้าใช้งานส่วนจัดการ')
                return redirect('accounts:login')

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงหน้านี้')
            raise PermissionDenied("สิทธิ์การใช้งานไม่เพียงพอ")
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """
    Restricts access strictly to Admin users.
    """
    return role_required(['admin'])(view_func)

def staff_or_admin_required(view_func):
    """
    Allows access to both Admin and Staff users.
    """
    return role_required(['admin', 'staff'])(view_func)

def limit_to_location(queryset, user, location_field='location'):
    """
    Filters a queryset based on user role and assigned location (FR32).
    - Admin: sees all locations
    - Staff: sees ONLY their assigned location
    """
    if user.is_shop_admin:
        return queryset
    if user.role == 'staff':
        if not user.location:
            return queryset.none()
        filter_kwargs = {location_field: user.location}
        return queryset.filter(**filter_kwargs)
    return queryset.none()
