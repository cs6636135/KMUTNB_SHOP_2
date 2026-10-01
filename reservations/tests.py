from django.test import TestCase, Client
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
from accounts.models import User
from shop.models import Category, Location, Product, Stock
from reservations.models import Reservation
from reservations.services import (
    create_reservation,
    expire_overdue_reservations,
    complete_pickup,
    cancel_reservation,
)

class KMUTNBShopComprehensiveTests(TestCase):
    def setUp(self):
        # 1. Create Locations
        self.loc_welfare = Location.objects.create(
            name='ร้านค้าสวัสดิการกลาง มจพ.',
            building='อาคาร 40',
            floor='1',
            room='ห้อง 101'
        )
        self.loc_eng = Location.objects.create(
            name='จุดจำหน่ายคณะวิศวกรรมศาสตร์',
            building='อาคาร 81',
            floor='2',
            room='ห้องสโมสร'
        )

        # 2. Create Users
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            password='password123',
            email='admin@kmutnb.ac.th',
            role=User.ROLE_ADMIN
        )

        self.staff_welfare = User.objects.create_user(
            username='staff_welfare_test',
            password='password123',
            role=User.ROLE_STAFF,
            location=self.loc_welfare,
            is_staff=True
        )

        self.staff_eng = User.objects.create_user(
            username='staff_eng_test',
            password='password123',
            role=User.ROLE_STAFF,
            location=self.loc_eng,
            is_staff=True
        )

        # 3. Create Categories & Products
        self.cat_uniform = Category.objects.create(name='เครื่องแบบและเครื่องประดับ')
        self.product_pin = Product.objects.create(
            category=self.cat_uniform,
            name='เข็มพระมหามงกุฎ มจพ.',
            price=120.00,
            reservable=True
        )
        self.product_umbrella = Product.objects.create(
            category=self.cat_uniform,
            name='ร่ม มจพ. (ซื้อหน้าร้านเท่านั้น)',
            price=200.00,
            reservable=False
        )

        # 4. Stock allocation
        self.stock_pin_welfare = Stock.objects.create(
            product=self.product_pin,
            location=self.loc_welfare,
            stock=10
        )
        self.stock_pin_eng = Stock.objects.create(
            product=self.product_pin,
            location=self.loc_eng,
            stock=5
        )

    # -------------------------------------------------------------
    # TC1: Product & Multi-Location Stock
    # -------------------------------------------------------------
    def test_tc1_product_and_multi_location_stock(self):
        """TC1: ตรวจสอบการคำนวณและแสดงสต็อกแยกตามสาขา (FR05, FR06)"""
        self.assertEqual(self.product_pin.total_stock, 15)
        self.assertEqual(self.product_pin.get_stock_at(self.loc_welfare), 10)
        self.assertEqual(self.product_pin.get_stock_at(self.loc_eng), 5)

    # -------------------------------------------------------------
    # TC2: Duplicate Product Name Prevention
    # -------------------------------------------------------------
    def test_tc2_duplicate_product_prevention(self):
        """TC2: ป้องกันการเพิ่มสินค้าชื่อซ้ำกัน (FR34)"""
        with self.assertRaises(Exception):
            Product.objects.create(
                category=self.cat_uniform,
                name='เข็มพระมหามงกุฎ มจพ.',
                price=150.00
            )

    # -------------------------------------------------------------
    # TC3: Non-reservable Product Check
    # -------------------------------------------------------------
    def test_tc3_non_reservable_product_cannot_be_reserved(self):
        """TC3: สินค้าที่ไม่เปิดให้จองล่วงหน้าต้องถูกปฏิเสธ (FR07)"""
        Stock.objects.create(product=self.product_umbrella, location=self.loc_welfare, stock=10)
        with self.assertRaises(ValidationError) as ctx:
            create_reservation(
                student_id='6604062636127',
                product_id=self.product_umbrella.id,
                location_id=self.loc_welfare.id,
                quantity=1
            )
        self.assertIn("ไม่เปิดให้ทำการจอง", str(ctx.exception))

    # -------------------------------------------------------------
    # TC4: Successful Reservation and Stock Deduction
    # -------------------------------------------------------------
    def test_tc4_successful_reservation_and_stock_deduction(self):
        """TC4: การจองสำเร็จ ระบบตัดสต็อกทันทีและกำหนดอายุ 4 ชั่วโมง (FR08, FR09, FR10, FR11)"""
        initial_stock = self.stock_pin_welfare.stock
        res = create_reservation(
            student_id='6604062636127',
            product_id=self.product_pin.id,
            location_id=self.loc_welfare.id,
            quantity=2
        )
        self.stock_pin_welfare.refresh_from_db()
        self.assertEqual(self.stock_pin_welfare.stock, initial_stock - 2)
        self.assertTrue(res.reservation_code.startswith("KMU-"))
        self.assertEqual(res.status, Reservation.STATUS_RESERVED)
        
        # Verify 4-hour window
        diff_hours = (res.expires_at - res.reserved_at).total_seconds() / 3600
        self.assertAlmostEqual(diff_hours, 4.0, places=1)

    # -------------------------------------------------------------
    # TC5: Overbooking Protection
    # -------------------------------------------------------------
    def test_tc5_cannot_reserve_exceeding_stock(self):
        """TC5: ระบบไม่อนุญาตให้จองสินค้าเกินสต็อกที่มีอยู่ (Non-functional 4)"""
        with self.assertRaises(ValidationError) as ctx:
            create_reservation(
                student_id='6604062636127',
                product_id=self.product_pin.id,
                location_id=self.loc_eng.id,
                quantity=10  # Only 5 available at eng branch
            )
        self.assertIn("ไม่เพียงพอ", str(ctx.exception))
        # Stock remains untouched
        self.stock_pin_eng.refresh_from_db()
        self.assertEqual(self.stock_pin_eng.stock, 5)

    # -------------------------------------------------------------
    # TC6: Expiration of Overdue Reservations & Auto Stock Return
    # -------------------------------------------------------------
    def test_tc6_overdue_reservation_expires_and_returns_stock(self):
        """TC6: รายการจองเกิน 4 ชั่วโมงเปลี่ยนเป็น Expired และคืนสต็อกอัตโนมัติ (FR13, FR14)"""
        res = create_reservation(
            student_id='6604062636127',
            product_id=self.product_pin.id,
            location_id=self.loc_welfare.id,
            quantity=3
        )
        self.stock_pin_welfare.refresh_from_db()
        self.assertEqual(self.stock_pin_welfare.stock, 7)

        # Simulate 4.5 hours elapsed
        past_time = timezone.now() - timedelta(minutes=10)
        res.expires_at = past_time
        res.save()

        # Run expiry service
        expired_count = expire_overdue_reservations()
        self.assertEqual(expired_count, 1)

        res.refresh_from_db()
        self.assertEqual(res.status, Reservation.STATUS_EXPIRED)

        # Stock refunded!
        self.stock_pin_welfare.refresh_from_db()
        self.assertEqual(self.stock_pin_welfare.stock, 10)

    # -------------------------------------------------------------
    # TC7: Pickup by Staff Workflow
    # -------------------------------------------------------------
    def test_tc7_staff_pickup_completion(self):
        """TC7: เจ้าหน้าที่ยืนยันรับสินค้า บันทึกเวลา และเปลี่ยนสถานะ (Workflow 2, FR30)"""
        res = create_reservation(
            student_id='6604062630315',
            product_id=self.product_pin.id,
            location_id=self.loc_welfare.id,
            quantity=1
        )
        complete_pickup(res.id, self.staff_welfare)
        res.refresh_from_db()
        self.assertEqual(res.status, Reservation.STATUS_PICKED_UP)
        self.assertIsNotNone(res.picked_up_at)

    # -------------------------------------------------------------
    # TC8: Staff Authorization Boundaries (FR30, FR32)
    # -------------------------------------------------------------
    def test_tc8_staff_cannot_manage_other_location(self):
        """TC8: Staff สาขาหนึ่งไม่สามารถตรวจรับหรือจัดการของสาขาอื่นได้ (FR30, FR32)"""
        # Welfare branch reservation
        res = create_reservation(
            student_id='6604062630315',
            product_id=self.product_pin.id,
            location_id=self.loc_welfare.id,
            quantity=1
        )
        # Attempt pickup by Engineering staff
        with self.assertRaises(PermissionDenied):
            complete_pickup(res.id, self.staff_eng)

    # -------------------------------------------------------------
    # TC9: Cancellation and Stock Return
    # -------------------------------------------------------------
    def test_tc9_cancellation_restores_stock(self):
        """TC9: ยกเลิกการจองก่อนหมดอายุ คืนสต็อกทันที"""
        res = create_reservation(
            student_id='6604062630315',
            product_id=self.product_pin.id,
            location_id=self.loc_eng.id,
            quantity=2
        )
        self.stock_pin_eng.refresh_from_db()
        self.assertEqual(self.stock_pin_eng.stock, 3)

        cancel_reservation(res.id, self.admin_user)
        res.refresh_from_db()
        self.assertEqual(res.status, Reservation.STATUS_CANCELLED)

        self.stock_pin_eng.refresh_from_db()
        self.assertEqual(self.stock_pin_eng.stock, 5)

    # -------------------------------------------------------------
    # TC10: Authentication and Authorization HTTP Route Protection
    # -------------------------------------------------------------
    def test_tc10_unauthenticated_cannot_access_manage_routes(self):
        """TC10: บุคคลทั่วไปเข้าถึงหน้าจัดการไม่ได้ ถูก Redirect ไปหน้า Login (FR24)"""
        client = Client()
        response = client.get('/manage/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/manage/login/', response.url)

    def test_tc11_staff_cannot_access_admin_product_management(self):
        """TC11: Staff ไม่สามารถเข้าหน้าสร้างสินค้าของ Admin ได้ (FR24)"""
        client = Client()
        client.force_login(self.staff_welfare)
        response = client.get('/manage/products/create/')
        self.assertEqual(response.status_code, 403)
