from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'ผู้ดูแลระบบ (Admin)'),
        (ROLE_STAFF, 'เจ้าหน้าที่ประจำสาขา (Staff)'),
    ]

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default=ROLE_STAFF,
        verbose_name='สิทธิ์ผู้ใช้งาน'
    )
    location = models.ForeignKey(
        'shop.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_users',
        verbose_name='สถานที่รับผิดชอบ'
    )

    class Meta:
        verbose_name = 'ผู้ใช้งาน'
        verbose_name_plural = 'ผู้ใช้งานทั้งหมด'
        ordering = ['username']

    def __str__(self):
        role_label = self.get_role_display()
        loc_label = f" ({self.location.name})" if self.location else ""
        return f"{self.username} [{role_label}{loc_label}]"

    @property
    def is_shop_admin(self):
        return self.is_superuser or self.role == self.ROLE_ADMIN

    @property
    def is_shop_staff(self):
        return self.role == self.ROLE_STAFF or self.is_shop_admin
