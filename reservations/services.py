from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
from shop.models import Product, Location, Stock
from .models import Reservation

def create_reservation(student_id: str, product_id: int, location_id: int, quantity: int = 1) -> Reservation:
    """
    Creates a new product reservation with concurrency-safe stock deduction (Workflow 1).
    Throws ValidationError if stock is insufficient or product is not reservable.
    """
    student_id = student_id.strip()
    if not student_id:
        raise ValidationError("กรุณาระบุรหัสนักศึกษาหรือเบอร์โทรศัพท์")

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValidationError("จำนวนที่จองต้องมากกว่า 0")
    except (ValueError, TypeError):
        raise ValidationError("จำนวนสินค้าไม่ถูกต้อง")

    # Atomic transaction with row locking
    with transaction.atomic():
        try:
            product = Product.objects.select_for_update().get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError("ไม่พบสินค้าที่ต้องการจอง")

        if not product.reservable:
            raise ValidationError("สินค้านี้ไม่เปิดให้ทำการจองล่วงหน้า")

        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise ValidationError("ไม่พบจุดจำหน่ายที่เลือก")

        try:
            stock_obj = Stock.objects.select_for_update().get(product=product, location=location)
        except Stock.DoesNotExist:
            raise ValidationError("สินค้านี้ไม่มีในสต็อกของจุดจำหน่ายที่เลือก")

        if stock_obj.stock < quantity:
            raise ValidationError(
                f"สินค้าไม่เพียงพอ มีคงเหลือ {stock_obj.stock} ชิ้น (คุณต้องการจอง {quantity} ชิ้น)"
            )

        # Deduct stock immediately
        stock_obj.stock -= quantity
        stock_obj.save()

        # Reservation expires in 4 hours
        expires_at = timezone.now() + timedelta(hours=4)

        reservation = Reservation.objects.create(
            student_id=student_id,
            product=product,
            location=location,
            quantity=quantity,
            status=Reservation.STATUS_RESERVED,
            expires_at=expires_at,
        )

    return reservation


def expire_overdue_reservations(location=None) -> int:
    """
    Finds reservations that have passed their 4-hour window (FR13)
    and returns the reserved stock back to the inventory (FR14).
    Returns the count of expired reservations processed.
    """
    now = timezone.now()
    qs = Reservation.objects.filter(
        status=Reservation.STATUS_RESERVED,
        expires_at__lte=now
    )
    if location:
        qs = qs.filter(location=location)

    expired_count = 0
    with transaction.atomic():
        for res in qs.select_for_update():
            res.status = Reservation.STATUS_EXPIRED
            res.save()

            # Return stock
            stock_obj, _ = Stock.objects.select_for_update().get_or_create(
                product=res.product,
                location=res.location,
                defaults={'stock': 0}
            )
            stock_obj.stock += res.quantity
            stock_obj.save()
            expired_count += 1

    return expired_count


def complete_pickup(reservation_id: int, user) -> Reservation:
    """
    Marks a reservation as picked up at the counter (Workflow 2, FR30).
    Verifies staff authorization and location match.
    """
    # Check expiry first
    expire_overdue_reservations()

    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().get(id=reservation_id)

        # Permission verification (FR30, FR32)
        if not user.is_shop_admin and user.role == 'staff':
            if reservation.location != user.location:
                raise PermissionDenied("คุณไม่มีสิทธิ์จัดการรายการจองของจุดจำหน่ายอื่น")

        if reservation.status != Reservation.STATUS_RESERVED:
            raise ValidationError(f"ไม่สามารถรับสินค้าได้เนื่องจากสถานะปัจจุบันคือ '{reservation.get_status_display()}'")

        if reservation.expires_at <= timezone.now():
            reservation.status = Reservation.STATUS_EXPIRED
            reservation.save()
            # Return stock
            stock_obj, _ = Stock.objects.select_for_update().get_or_create(
                product=reservation.product,
                location=reservation.location,
                defaults={'stock': 0}
            )
            stock_obj.stock += reservation.quantity
            stock_obj.save()
            raise ValidationError("รายการจองนี้หมดอายุเกิน 4 ชั่วโมงแล้ว สินค้าถูกคืนสู่สต็อกเรียบร้อยแล้ว")

        reservation.status = Reservation.STATUS_PICKED_UP
        reservation.picked_up_at = timezone.now()
        reservation.save()

    return reservation


def cancel_reservation(reservation_id: int, user) -> Reservation:
    """
    Cancels a reservation and restores the reserved quantity to the stock.
    """
    with transaction.atomic():
        reservation = Reservation.objects.select_for_update().get(id=reservation_id)

        # Authorization check
        if not user.is_shop_admin and user.role == 'staff':
            if reservation.location != user.location:
                raise PermissionDenied("คุณไม่มีสิทธิ์ยกเลิกรายการจองของจุดจำหน่ายอื่น")

        if reservation.status == Reservation.STATUS_RESERVED:
            # Restore stock
            stock_obj, _ = Stock.objects.select_for_update().get_or_create(
                product=reservation.product,
                location=reservation.location,
                defaults={'stock': 0}
            )
            stock_obj.stock += reservation.quantity
            stock_obj.save()

        reservation.status = Reservation.STATUS_CANCELLED
        reservation.save()

    return reservation
