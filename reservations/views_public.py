from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Reservation
from .forms import ReservationForm, LookupForm
from .services import create_reservation, expire_overdue_reservations
from shop.models import Product

def reserve_action(request):
    """
    Submits a reservation from public interface
    """
    if request.method != 'POST':
        return redirect('shop:product_list')

    form = ReservationForm(request.POST)
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    if form.is_valid():
        student_id = form.cleaned_data['student_id']
        location_id = form.cleaned_data['location_id']
        quantity = form.cleaned_data['quantity']

        try:
            reservation = create_reservation(
                student_id=student_id,
                product_id=product.id,
                location_id=location_id,
                quantity=quantity
            )
            messages.success(request, f'จองสินค้าสำเร็จ! รหัสการจองของคุณคือ {reservation.reservation_code}')
            return redirect('reservations:reserve_success', code=reservation.reservation_code)
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
            return redirect('shop:product_detail', product_id=product.id)
    else:
        messages.error(request, 'ข้อมูลการจองไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')
        return redirect('shop:product_detail', product_id=product.id)


def reserve_success(request, code):
    # Ensure expired items get updated
    expire_overdue_reservations()
    reservation = get_object_or_404(
        Reservation.objects.select_related('product', 'location'),
        reservation_code=code
    )
    return render(request, 'reservations/reserve.html', {
        'reservation': reservation,
    })


def status_lookup_view(request):
    """
    Lookup reservation history by Student ID or Reservation Code (FR12).
    Supports HTMX live results.
    """
    expire_overdue_reservations()
    query = request.GET.get('query', '').strip()
    reservations = []

    if query:
        reservations = Reservation.objects.select_related('product', 'location').filter(
            Q(student_id__iexact=query) | Q(reservation_code__iexact=query)
        ).order_by('-reserved_at')

    context = {
        'query': query,
        'reservations': reservations,
    }

    if request.headers.get('HX-Request') and not request.headers.get('HX-Boosted'):
        return render(request, 'partials/reservation_list.html', context)

    return render(request, 'reservations/status.html', context)
