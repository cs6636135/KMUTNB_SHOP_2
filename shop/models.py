from django.db import models
from django.db.models import Sum

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='ชื่อหมวดหมู่')
    description = models.TextField(blank=True, verbose_name='รายละเอียดหมวดหมู่')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่สร้าง')

    class Meta:
        verbose_name = 'หมวดหมู่สินค้า'
        verbose_name_plural = 'หมวดหมู่สินค้าทั้งหมด'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=150, verbose_name='ชื่อจุดจำหน่าย')
    building = models.CharField(max_length=100, blank=True, verbose_name='ชื่อ/เลขอาคาร')
    floor = models.CharField(max_length=30, blank=True, verbose_name='ชั้น')
    room = models.CharField(max_length=100, blank=True, verbose_name='ห้องหรือบริเวณ')
    description = models.TextField(blank=True, verbose_name='รายละเอียดสถานที่')

    class Meta:
        verbose_name = 'สถานที่จำหน่าย'
        verbose_name_plural = 'สถานที่จำหน่ายทั้งหมด'
        ordering = ['name']

    def __str__(self):
        parts = [self.name]
        loc_details = []
        if self.building:
            loc_details.append(self.building)
        if self.floor:
            loc_details.append(f"ชั้น {self.floor}")
        if self.room:
            loc_details.append(self.room)
        if loc_details:
            return f"{self.name} ({', '.join(loc_details)})"
        return self.name

    @property
    def location_detail(self):
        details = []
        if self.building:
            details.append(f"อาคาร {self.building}")
        if self.floor:
            details.append(f"ชั้น {self.floor}")
        if self.room:
            details.append(f"ห้อง {self.room}")
        return " • ".join(details) if details else "จุดจำหน่ายหลัก"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='หมวดหมู่'
    )
    name = models.CharField(max_length=150, unique=True, verbose_name='ชื่อสินค้า')
    description = models.TextField(blank=True, verbose_name='รายละเอียดสินค้า')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='ราคาสินค้า (บาท)')
    image_url = models.CharField(max_length=500, blank=True, verbose_name='URL รูปภาพสินค้า')
    reservable = models.BooleanField(
        default=True,
        verbose_name='สินค้ารองรับการจอง',
        help_text='1 = รองรับการจอง, 0 = ไม่รองรับการจอง'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='วันที่เพิ่มสินค้า')

    class Meta:
        verbose_name = 'สินค้า'
        verbose_name_plural = 'สินค้าทั้งหมด'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (฿{self.price:,.2f})"

    @property
    def total_stock(self):
        res = self.stocks.aggregate(total=Sum('stock'))['total']
        return res if res is not None else 0

    def get_stock_at(self, location):
        stock_obj = self.stocks.filter(location=location).first()
        return stock_obj.stock if stock_obj else 0


class Stock(models.Model):
    """
    ตาราง product_locations ตามเอกสาร
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='สินค้า'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name='สถานที่จำหน่าย'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='จำนวนคงเหลือ')

    class Meta:
        db_table = 'product_locations'
        verbose_name = 'สต็อกสินค้าตามสถานที่'
        verbose_name_plural = 'สต็อกสินค้าตามสถานที่ทั้งหมด'
        unique_together = ('product', 'location')
        ordering = ['location', 'product']

    def __str__(self):
        return f"{self.product.name} @ {self.location.name} = {self.stock} ชิ้น"
