from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from accounts.permissions import staff_or_admin_required, limit_to_location
from shop.models import Location
from .models import Reservation
from .services import complete_pickup, cancel_reservation, expire_overdue_reservations

@staff_or_admin_required
def reservations_list_manage(request):
    user = request.user
    is_admin = user.is_shop_admin

    # Automatically check expired entries
    expire_overdue_reservations()

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    location_filter = request.GET.get('location', '').strip()

    reservations = Reservation.objects.select_related('product', 'location')

    if is_admin:
        locations = Location.objects.all()
        if location_filter:
            reservations = reservations.filter(location_id=location_filter)
    else:
        # Staff is strictly locked to their location (FR29, FR32)
        locations = Location.objects.filter(pk=user.location_id) if user.location else Location.objects.none()
        reservations = reservations.filter(location=user.location)

    if status_filter:
        reservations = reservations.filter(status=status_filter)

    if query:
        reservations = reservations.filter(
            Q(reservation_code__icontains=query) |
            Q(student_id__icontains=query) |
            Q(product__name__icontains=query)
        )

    context = {
        'reservations': reservations,
        'locations': locations,
        'is_admin': is_admin,
        'user_location': user.location,
        'status_filter': status_filter,
        'location_filter': location_filter,
        'query': query,
    }
    return render(request, 'manage/reservations.html', context)


@staff_or_admin_required
@require_http_methods(['POST'])
def mark_pickup_manage(request, reservation_id):
    try:
        res = complete_pickup(reservation_id, request.user)
        messages.success(
            request,
            f'บันทึกรับสินค้าสำเร็จ! รหัส {res.reservation_code} (ผู้รับ: {res.student_id})'
        )
    except (ValidationError, PermissionDenied) as e:
        messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('reservations_manage:reservation_list')


@staff_or_admin_required
@require_http_methods(['POST'])
def cancel_reservation_manage(request, reservation_id):
    try:
        res = cancel_reservation(reservation_id, request.user)
        messages.info(
            request,
            f'ยกเลิกรายการจอง {res.reservation_code} และคืนสต็อกเรียบร้อยแล้ว'
        )
    except (ValidationError, PermissionDenied) as e:
        messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('reservations_manage:reservation_list')
