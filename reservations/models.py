import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Reservation(models.Model):
    STATUS_RESERVED = 'reserved'
    STATUS_PICKED_UP = 'picked_up'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_RESERVED, 'จองแล้ว (Reserved)'),
        (STATUS_PICKED_UP, 'รับสินค้าแล้ว (Picked Up)'),
        (STATUS_EXPIRED, 'หมดอายุ (Expired)'),
        (STATUS_CANCELLED, 'ยกเลิก (Cancelled)'),
    ]

    reservation_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='รหัสการจอง'
    )
    student_id = models.CharField(
        max_length=20,
        verbose_name='รหัสนักศึกษา / เบอร์โทร'
    )
    product = models.ForeignKey(
        'shop.Product',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='สินค้า'
    )
    location = models.ForeignKey(
        'shop.Location',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='สถานที่รับสินค้า'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='จำนวนที่จอง'
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_RESERVED,
        verbose_name='สถานะการจอง'
    )
    reserved_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='เวลาที่จอง'
    )
    expires_at = models.DateTimeField(
        verbose_name='เวลาหมดอายุ'
    )
    picked_up_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='เวลารับสินค้า'
    )

    class Meta:
        db_table = 'reservations'
        verbose_name = 'รายการจองสินค้า'
        verbose_name_plural = 'รายการจองสินค้าทั้งหมด'
        ordering = ['-reserved_at']

    def __str__(self):
        return f"{self.reservation_code} - {self.student_id} ({self.product.name} x {self.quantity})"

    def save(self, *args, **kwargs):
        if not self.reservation_code:
            short_id = uuid.uuid4().hex[:6].upper()
            date_str = timezone.now().strftime('%m%d')
            self.reservation_code = f"KMU-{date_str}-{short_id}"
        if not self.expires_at:
            # Default expiry: 4 hours from now (FR11)
            self.expires_at = timezone.now() + timedelta(hours=4)
        super().save(*args, **kwargs)

    @property
    def is_expired_now(self):
        return self.status == self.STATUS_RESERVED and timezone.now() > self.expires_at

    @property
    def remaining_seconds(self):
        if self.status != self.STATUS_RESERVED:
            return 0
        diff = (self.expires_at - timezone.now()).total_seconds()
        return max(0, int(diff))

    @property
    def status_color(self):
        colors = {
            self.STATUS_RESERVED: 'bg-amber-100 text-amber-800 border-amber-300',
            self.STATUS_PICKED_UP: 'bg-emerald-100 text-emerald-800 border-emerald-300',
            self.STATUS_EXPIRED: 'bg-rose-100 text-rose-800 border-rose-300',
            self.STATUS_CANCELLED: 'bg-slate-100 text-slate-700 border-slate-300',
        }
        return colors.get(self.status, 'bg-slate-100 text-slate-700 border-slate-300')

    @property
    def total_price(self):
        return self.product.price * self.quantity
