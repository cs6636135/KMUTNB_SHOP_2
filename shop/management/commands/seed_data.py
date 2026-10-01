import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Location, Product, Stock
from reservations.models import Reservation
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial sample data for KMUTNB Shop system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=== เริ่มต้นการนำเข้าข้อมูลจำลอง KMUTNB Shop ==='))

        # 1. Locations
        loc_data = [
            {
                'name': 'ร้านค้าสวัสดิการกลาง มจพ.',
                'building': 'อาคาร 40',
                'floor': '1',
                'room': 'ห้องสวัสดิการนักศึกษา',
                'description': 'ศูนย์รวมเครื่องแบบ อุปกรณ์นักศึกษา และของใช้ทั่วไปใจกลางมหาวิทยาลัย'
            },
            {
                'name': 'จุดจำหน่ายคณะวิศวกรรมศาสตร์',
                'building': 'อาคาร 81',
                'floor': '2',
                'room': 'ห้องกิจกรรมสโมสรนักศึกษา',
                'description': 'จุดจำหน่ายเสื้อช็อป อุปกรณ์ช่าง และของที่ระลึกประจำคณะวิศวะ'
            },
            {
                'name': 'ศูนย์หนังสือพระจอมเกล้าพระนครเหนือ',
                'building': 'อาคารอเนกประสงค์',
                'floor': '3',
                'room': 'ห้องสมุดและศูนย์หนังสือ',
                'description': 'แหล่งรวมตำราเรียน เอกสารคำสอน และอุปกรณ์การศึกษาระดับอุดมศึกษา'
            },
            {
                'name': 'จุดบริการวิทยาศาสตร์ประยุกต์',
                'building': 'อาคาร 78',
                'floor': '1',
                'room': 'โถงชั้น 1 หน้าภาควิชา CS',
                'description': 'จุดบริการและรับสินค้าสำหรับนักศึกษาคณะวิทยาศาสตร์ประยุกต์'
            }
        ]

        locations = {}
        for item in loc_data:
            loc, _ = Location.objects.get_or_create(name=item['name'], defaults=item)
            locations[loc.name] = loc
            self.stdout.write(f'  [+] จุดจำหน่าย: {loc.name}')

        # 2. Categories
        cat_data = [
            {'name': 'เครื่องแบบและเครื่องประดับนักศึกษา', 'description': 'เข็มพระมหามงกุฎ ติ้ง กระดุม หัวเข็มขัด และเนคไท'},
            {'name': 'เสื้อช็อปและเสื้อกิจกรรมคณะ', 'description': 'เสื้อช็อปปฏิบัติการ เสื้อโปโลคณะ และแจ็คเก็ตมหาวิทยาลัย'},
            {'name': 'หนังสือและเอกสารประกอบการเรียน', 'description': 'ตำราเรียนวิชาพื้นฐานและวิชาเฉพาะทางวิศวกรรมและวิทยาศาสตร์'},
            {'name': 'เครื่องเขียนและของที่ระลึก มจพ.', 'description': 'สมุดตราพระจอมเกล้า ปากกา กระบอกน้ำ และของที่ระลึก'},
        ]

        categories = {}
        for item in cat_data:
            cat, _ = Category.objects.get_or_create(name=item['name'], defaults=item)
            categories[cat.name] = cat
            self.stdout.write(f'  [+] หมวดหมู่: {cat.name}')

        # 3. Products
        prod_data = [
            {
                'name': 'เข็มติดหน้าอก พระมหามงกุฎ มจพ. (ชุบทองคำแท้)',
                'category': categories['เครื่องแบบและเครื่องประดับนักศึกษา'],
                'price': 120.00,
                'description': 'ตราสัญลักษณ์พระมหามงกุฎสำหรับประดับหน้าอกเสื้อนักศึกษาหญิง มจพ. งานลงยาสวยงาม ถูกต้องตามระเบียบมหาวิทยาลัย',
                'image_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 45,
                    'จุดจำหน่ายคณะวิศวกรรมศาสตร์': 20,
                    'จุดบริการวิทยาศาสตร์ประยุกต์': 15,
                }
            },
            {
                'name': 'เนคไทนักศึกษาตราพระมหามงกุฎ (สีแดงเลือดหมู-ส้ม)',
                'category': categories['เครื่องแบบและเครื่องประดับนักศึกษา'],
                'price': 180.00,
                'description': 'เนคไทผ้าไหมเทียมทอละเอียด สีกรมท่าสลับแถบสีแดงหมากสุก ปักตราสัญลักษณ์คมชัด สำหรับชุดพิธีการ',
                'image_url': 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 30,
                    'จุดจำหน่ายคณะวิศวกรรมศาสตร์': 15,
                }
            },
            {
                'name': 'หัวเข็มขัดและสายเข็มขัดหนังสีดำ มจพ.',
                'category': categories['เครื่องแบบและเครื่องประดับนักศึกษา'],
                'price': 150.00,
                'description': 'หัวเข็มขัดโลหะรมดำปั๊มนูนตราพระมหามงกุฎ พร้อมสายหนังคุณภาพดี แข็งแรง ทนทาน ถูกระเบียบ',
                'image_url': 'https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 50,
                    'ศูนย์หนังสือพระจอมเกล้าพระนครเหนือ': 25,
                }
            },
            {
                'name': 'เสื้อช็อปวิศวกรรมศาสตร์ KMUTNB (สีกรมท่าเข้ม)',
                'category': categories['เสื้อช็อปและเสื้อกิจกรรมคณะ'],
                'price': 450.00,
                'description': 'เสื้อช็อปผ้าคอมทวิวเนื้อหนา ระบายอากาศดี ปักตราฟันเฟืองและพระมหามงกุฎบริเวณอกซ้าย ช่องเสียบปากกาที่แขน',
                'image_url': 'https://images.unsplash.com/photo-1578932750294-f5075e85f44a?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 12,
                    'จุดจำหน่ายคณะวิศวกรรมศาสตร์': 28,
                }
            },
            {
                'name': 'เสื้อช็อปภาควิชาวิทยาการคอมพิวเตอร์และสารสนเทศ (CS KMUTNB)',
                'category': categories['เสื้อช็อปและเสื้อกิจกรรมคณะ'],
                'price': 420.00,
                'description': 'เสื้อช็อปสีเทาเข้มปักโลโก้ CS Applied Science สวมใส่สบายสำหรับแล็บคอมพิวเตอร์และการฝึกปฏิบัติงาน',
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'จุดบริการวิทยาศาสตร์ประยุกต์': 25,
                    'ร้านค้าสวัสดิการกลาง มจพ.': 5,
                }
            },
            {
                'name': 'หนังสือ Data Structures & Algorithms ฉบับภาษาไทย',
                'category': categories['หนังสือและเอกสารประกอบการเรียน'],
                'price': 290.00,
                'description': 'ตำราโครงสร้างข้อมูลและขั้นตอนวิธี ครอบคลุมตั้งแต่ Array, Linked List, Tree จนถึง Graph พร้อมโค้ดตัวอย่าง Python/C++',
                'image_url': 'https://images.unsplash.com/photo-1532012164546-f432f2e3777f?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ศูนย์หนังสือพระจอมเกล้าพระนครเหนือ': 40,
                    'จุดบริการวิทยาศาสตร์ประยุกต์': 10,
                }
            },
            {
                'name': 'สมุดเลคเชอร์ปกแข็ง ตราพระจอมเกล้าพระนครเหนือ (สันห่วง)',
                'category': categories['เครื่องเขียนและของที่ระลึก มจพ.'],
                'price': 65.00,
                'description': 'สมุดโน้ตกระดาษถนอมสายตา 80 แกรม จำนวน 120 แผ่น ตีเส้นบรรทัดพร้อมเส้นกั้นหน้า ปกแข็งพิมพ์ฟอยล์ส้มทอง',
                'image_url': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 80,
                    'ศูนย์หนังสือพระจอมเกล้าพระนครเหนือ': 60,
                    'จุดจำหน่ายคณะวิศวกรรมศาสตร์': 30,
                    'จุดบริการวิทยาศาสตร์ประยุกต์': 20,
                }
            },
            {
                'name': 'กระบอกน้ำสแตนเลสเก็บความเย็น KMUTNB Edition (500 ml)',
                'category': categories['เครื่องเขียนและของที่ระลึก มจพ.'],
                'price': 320.00,
                'description': 'กระบอกน้ำเก็บอุณหภูมิร้อน-เย็นได้ 24 ชั่วโมง สแตนเลส Food Grade 316 เลเซอร์สัญลักษณ์ KMUTNB สีส้มพรีเมียม',
                'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&auto=format&fit=crop&q=80',
                'reservable': True,
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 18,
                    'จุดจำหน่ายคณะวิศวกรรมศาสตร์': 8,
                }
            },
            {
                'name': 'ร่มพับกันแสง UV อัตโนมัติ ตราพระเกี้ยว/พระมหามงกุฎ',
                'category': categories['เครื่องเขียนและของที่ระลึก มจพ.'],
                'price': 220.00,
                'description': 'ร่มพับเปิด-ปิดอัตโนมัติ ก้านคาร์บอนไฟเบอร์แข็งแรง ทนทานต่อลมและฝน เคลือบสารสะท้อนรังสี UV 99% (สินค้าซื้อหน้างานเท่านั้น)',
                'image_url': 'https://images.unsplash.com/photo-1534353436294-0dbd4bdac845?w=600&auto=format&fit=crop&q=80',
                'reservable': False,  # Non-reservable demonstration
                'stocks': {
                    'ร้านค้าสวัสดิการกลาง มจพ.': 15,
                }
            }
        ]

        for item in prod_data:
            stocks_info = item.pop('stocks')
            prod, _ = Product.objects.get_or_create(name=item['name'], defaults=item)
            for loc_name, qty in stocks_info.items():
                loc_obj = locations[loc_name]
                Stock.objects.update_or_create(
                    product=prod,
                    location=loc_obj,
                    defaults={'stock': qty}
                )
            self.stdout.write(f'  [+] สินค้า: {prod.name}')

        # 4. Users (Admin and Branch Staff)
        # Admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'ผู้ดูแลระบบ',
                'last_name': 'กลาง มจพ.',
                'email': 'admin@kmutnb.ac.th',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin1234')
        admin_user.role = User.ROLE_ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'  [✓] สร้าง Admin: admin / admin1234'))

        # Staff 1: Welfare Central Shop (Building 40)
        staff_welfare, created = User.objects.get_or_create(
            username='staff_welfare',
            defaults={
                'first_name': 'เจ้าหน้าที่',
                'last_name': 'ร้านสวัสดิการกลาง',
                'email': 'welfare@kmutnb.ac.th',
                'role': User.ROLE_STAFF,
                'location': locations['ร้านค้าสวัสดิการกลาง มจพ.'],
                'is_staff': True,
            }
        )
        staff_welfare.set_password('staff1234')
        staff_welfare.location = locations['ร้านค้าสวัสดิการกลาง มจพ.']
        staff_welfare.role = User.ROLE_STAFF
        staff_welfare.is_staff = True
        staff_welfare.save()
        self.stdout.write(self.style.SUCCESS(f'  [✓] สร้าง Staff: staff_welfare / staff1234 (ร้านสวัสดิการกลาง)'))

        # Staff 2: Engineering Shop (Building 81)
        staff_eng, created = User.objects.get_or_create(
            username='staff_eng',
            defaults={
                'first_name': 'เจ้าหน้าที่',
                'last_name': 'สโมสรวิศวะ',
                'email': 'eng_shop@kmutnb.ac.th',
                'role': User.ROLE_STAFF,
                'location': locations['จุดจำหน่ายคณะวิศวกรรมศาสตร์'],
                'is_staff': True,
            }
        )
        staff_eng.set_password('staff1234')
        staff_eng.location = locations['จุดจำหน่ายคณะวิศวกรรมศาสตร์']
        staff_eng.role = User.ROLE_STAFF
        staff_eng.is_staff = True
        staff_eng.save()
        self.stdout.write(self.style.SUCCESS(f'  [✓] สร้าง Staff: staff_eng / staff1234 (วิศวกรรมศาสตร์)'))

        # 5. Sample Reservations for demonstration
        p1 = Product.objects.get(name__startswith='เข็มติดหน้าอก')
        l1 = locations['ร้านค้าสวัสดิการกลาง มจพ.']
        r1, _ = Reservation.objects.get_or_create(
            reservation_code='KMU-1001-A9F2',
            defaults={
                'student_id': '6604062636127',
                'product': p1,
                'location': l1,
                'quantity': 1,
                'status': Reservation.STATUS_RESERVED,
                'expires_at': timezone.now() + timedelta(hours=3, minutes=45),
            }
        )

        p2 = Product.objects.get(name__startswith='เสื้อช็อปวิศวกรรมศาสตร์')
        l2 = locations['จุดจำหน่ายคณะวิศวกรรมศาสตร์']
        r2, _ = Reservation.objects.get_or_create(
            reservation_code='KMU-1001-B3K8',
            defaults={
                'student_id': '6604062630315',
                'product': p2,
                'location': l2,
                'quantity': 2,
                'status': Reservation.STATUS_PICKED_UP,
                'expires_at': timezone.now() - timedelta(hours=1),
                'picked_up_at': timezone.now() - timedelta(minutes=30),
            }
        )

        self.stdout.write(self.style.SUCCESS('=== สำเร็จ! นำเข้าข้อมูลตัวอย่าง KMUTNB Shop ครบถ้วน ==='))
