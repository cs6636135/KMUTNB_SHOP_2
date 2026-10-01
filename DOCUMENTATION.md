# เอกสารโครงการ: ระบบค้นหาและจองสินค้าภายในมหาวิทยาลัย (KMUTNB Shop)

**มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ**  
ภาควิชาวิทยาการคอมพิวเตอร์และสารสนเทศ คณะวิทยาศาสตร์ประยุกต์  
ภาคการศึกษาที่ 1 ปีการศึกษา 2569  

---

## 1. บทนำและวัตถุประสงค์โครงการ (Project Overview)

ปัจจุบันภายในมหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ (มจพ.) มีสินค้า เครื่องแบบ เครื่องประดับ และตำราเรียน จำหน่ายอยู่ตามจุดต่างๆ เช่น ร้านค้าสวัสดิการกลาง (อาคาร 40), สโมสรคณะวิศวกรรมศาสตร์ (อาคาร 81), ศูนย์หนังสือ และจุดบริการวิทยาศาสตร์ประยุกต์ ทำให้เกิดปัญหา:
1. ผู้ใช้งานไม่ทราบว่าสินค้ามีจำหน่ายที่ใด และมีจำนวนคงเหลือในแต่ละจุดเท่าใด
2. สินค้าชนิดเดียวกันอาจมีจำนวนคงเหลือไม่เท่ากันในแต่ละสาขา
3. นักศึกษาเดินทางไปแล้วพบว่าสินค้าหมดสต็อก

**KMUTNB Shop** จึงถูกพัฒนาขึ้นเพื่อให้ผู้ใช้สามารถ:
- ค้นหา ดูรายละเอียด ราคา และเช็คสต็อกสินค้าแยกตามจุดจำหน่ายในมหาวิทยาลัย
- จองสินค้าออนไลน์ล่วงหน้า ล็อกสต็อกทันทีด้วยรหัสการจอง และกำหนดเวลารับสินค้าภายใน **4 ชั่วโมง**
- แบ่งแยกสิทธิ์การบริหารจัดการระหว่าง **Admin (ผู้ดูแลระบบกลาง)** และ **Staff (เจ้าหน้าที่ประจำจุดจำหน่าย)** ได้อย่างรัดกุม ปลอดภัย

---

## 2. สถาปัตยกรรมและเทคโนโลยีที่ใช้ (Tech Stack & Architecture)

- **Backend Framework:** Django 6.1 (Python 3.13)
- **Frontend Interaction:** HTMX (สำหรับ instant search, category filtering, live updates โดยไม่ต้องโหลดทั้งหน้าใหม่)
- **Styling:** Tailwind CSS (ผ่าน CDN พร้อม Palette สีประจำมหาวิทยาลัยพระจอมเกล้าพระนครเหนือ: สีแดงหมากสุก `#E04006`)
- **Database & ORM:** Django ORM พร้อมรองรับ ACID Transactions, Row Locking (`select_for_update()`) และ Rollback
- **Security:**
  - Django CSRF Protection บน Form และ HTMX Headers
  - XSS Protection อัตโนมัติด้วย Django Template Engine
  - Clickjacking Protection (`X-Frame-Options: DENY`)
  - Session-based Authentication พร้อม Password Hashing (PBKDF2)

---

## 3. โครงสร้างโฟลเดอร์ของโปรเจกต์ (Project Structure)

```text
kmutnb_shop/
├── manage.py
├── requirements.txt
├── test_report.html             # รายงานผลการทดสอบ HTML (เปิดดูในเบราว์เซอร์ได้)
├── DOCUMENTATION.md             # เอกสารฉบับนี้
├── config/
│   ├── settings.py
│   ├── urls.py                  # / = หน้าบ้าน, /manage/ = หลังบ้าน, /admin/ = Django Admin
│   └── wsgi.py
├── accounts/
│   ├── models.py                # User (AbstractUser + role + location)
│   ├── permissions.py           # @role_required, @admin_required, limit_to_location
│   ├── forms.py                 # LoginForm, StaffForm
│   ├── views.py                 # login, logout, จัดการ Staff (admin)
│   ├── urls.py
│   └── admin.py
├── shop/
│   ├── models.py                # Category, Product, Location, Stock (product_locations)
│   ├── forms.py                 # CategoryForm, ProductForm, LocationForm, StockForm
│   ├── views_public.py          # ค้นหาสินค้า, หน้าแรก, หน้ารายละเอียดสินค้า
│   ├── views_manage.py          # CRUD สินค้า, หมวดหมู่, จุดจำหน่าย, สต็อก
│   ├── urls.py
│   ├── manage_urls.py
│   └── admin.py
├── reservations/
│   ├── models.py                # Reservation (รหัสการจอง, สถานะ, เวลาหมดอายุ 4 ชม.)
│   ├── services.py              # จองสินค้า, ตัด/คืนสต็อก, ตรวจสอบหมดอายุอัตโนมัติ
│   ├── forms.py                 # ReservationForm, LookupForm
│   ├── views_public.py          # ยืนยันการจอง, สลิปตั๋ว 4 ชม., ตรวจสอบสถานะการจอง
│   ├── views_manage.py          # รายการจอง, รับสินค้า, ยกเลิก
│   ├── urls.py
│   ├── manage_urls.py
│   └── tests.py                 # ชุดทดสอบ Unit & Integration Tests (TC1 - TC11)
├── templates/
│   ├── base.html                # Tailwind + HTMX + CSRF Header + Mobile Nav
│   ├── base_manage.html         # Layout ระบบจัดการหลังบ้าน + Sidebar
│   ├── test_report.html         # เทมเพลตหน้ารายงานผลการทดสอบ
│   ├── partials/                # ชิ้นส่วนสำหรับ HTMX Swap
│   │   ├── product_list.html
│   │   ├── product_card.html
│   │   ├── reservation_list.html
│   │   └── status_badge.html
│   ├── shop/
│   │   ├── home.html
│   │   ├── products.html
│   │   └── product_detail.html
│   ├── reservations/
│   │   ├── reserve.html         # สลิปการจองพร้อมเวลานับถอยหลัง 4 ชม.
│   │   └── status.html          # ค้นหาด้วยรหัสนักศึกษา / รหัสการจอง
│   └── manage/
│       ├── login.html           # เข้าสู่ระบบพร้อมปุ่มทดสอบ One-click
│       ├── dashboard.html       # แดชบอร์ดภาพรวม (Admin ดูทั้งหมด, Staff ดูเฉพาะสาขาตนเอง)
│       ├── products.html
│       ├── product_form.html
│       ├── categories.html
│       ├── category_form.html
│       ├── locations.html
│       ├── location_form.html
│       ├── stock.html
│       ├── stock_form.html
│       ├── reservations.html
│       ├── staff.html
│       └── staff_form.html
└── static/
    ├── css/output.css
    └── images/
```

---

## 4. โครงสร้างฐานข้อมูล (Database Schema & ER Relationships)

### 4.1 ตารางผู้ใช้งาน (`users` / `accounts_user`)
- สืบทอดจาก `AbstractUser` ของ Django
- `role`: `admin` (ผู้ดูแลระบบ) หรือ `staff` (เจ้าหน้าที่ประจำสาขา)
- `location_id`: เชื่อมโยงไปยัง `Location` (หากเป็น null หมายถึง Admin ประจำส่วนกลาง)

### 4.2 ตารางหมวดหมู่สินค้า (`categories` / `shop_category`)
- `id`: Primary Key
- `name`: ชื่อหมวดหมู่ (Unique)
- `description`: รายละเอียด

### 4.3 ตารางสินค้า (`products` / `shop_product`)
- `id`: Primary Key
- `category_id`: Foreign Key ไปยัง Category
- `name`: ชื่อสินค้า (Unique ป้องกันชื่อซ้ำ FR34)
- `description`: รายละเอียดสินค้า
- `price`: ราคาสินค้า (ทศนิยม 2 ตำแหน่ง)
- `image_url`: ที่อยู่รูปภาพสินค้า
- `reservable`: เปิดให้จองออนไลน์หรือไม่ (True/False)
- `created_at`: วันที่เพิ่มสินค้า

### 4.4 ตารางสถานที่จำหน่าย (`locations` / `shop_location`)
- `id`: Primary Key
- `name`: ชื่อจุดจำหน่าย (เช่น ร้านค้าสวัสดิการกลาง มจพ., อาคาร 81 วิศวะ)
- `building`: ชื่อ/เลขอาคาร
- `floor`: ชั้น
- `room`: ห้องหรือบริเวณ
- `description`: รายละเอียดการเดินทาง

### 4.5 ตารางสต็อกสินค้าตามสถานที่ (`product_locations`)
- `product_id`: Foreign Key ไปยัง Product
- `location_id`: Foreign Key ไปยัง Location
- `stock`: จำนวนสินค้าคงเหลือในจุดจำหน่ายนั้น
- *Constraint:* `unique_together = ('product', 'location')`

### 4.6 ตารางการจองสินค้า (`reservations`)
- `id`: Primary Key
- `reservation_code`: รหัสการจองเฉพาะตัว (Unique เช่น `KMU-1001-A9F2`)
- `student_id`: รหัสนักศึกษา หรือ เบอร์โทรศัพท์
- `product_id`: Foreign Key ไปยัง Product
- `location_id`: Foreign Key ไปยัง Location ที่เลือกไปรับของ
- `quantity`: จำนวนที่จอง
- `status`: `reserved` (จองแล้ว), `picked_up` (รับสินค้าแล้ว), `expired` (หมดเวลา 4 ชม.), `cancelled` (ยกเลิก)
- `reserved_at`: เวลาที่ทำรายการ
- `expires_at`: เวลาหมดอายุ (นับจากเวลาจอง + 4 ชั่วโมง)
- `picked_up_at`: เวลาที่เจ้าหน้าที่กดบันทึกรับสินค้า

---

## 5. ตารางตรวจสอบฟังก์ชันการทำงาน (Functional Requirements Coverage)

| รหัส | ข้อกำหนด (Requirement) | สถานะ | ไฟล์ที่รับผิดชอบ |
|---|---|:---:|---|
| **FR01** | แสดงรายการสินค้าที่มีอยู่ในระบบได้ | ✓ | `shop/views_public.py` (`products_view`) |
| **FR02** | แสดงรายละเอียดสินค้า (ชื่อ, รายละเอียด, ราคา) | ✓ | `shop/views_public.py` (`product_detail_view`) |
| **FR03** | ค้นหาสินค้าจากชื่อสินค้าได้ (Instant Search) | ✓ | `shop/views_public.py` + HTMX |
| **FR04** | กรองสินค้าตามหมวดหมู่ได้ | ✓ | `shop/views_public.py` |
| **FR05** | แสดงสถานที่จำหน่ายของสินค้าได้ | ✓ | `shop/views_public.py` (`product_detail.html`) |
| **FR06** | แสดงจำนวนสต็อกคงเหลือแยกตามสถานที่จำหน่ายได้ | ✓ | `shop/views_public.py` (`stocks` breakdown) |
| **FR07** | แสดงสินค้าที่รองรับและไม่รองรับการจองได้ | ✓ | `shop/models.py` (`reservable` field) |
| **FR08** | ผู้ใช้กรอกรหัสนักศึกษาเพื่อจองสินค้าได้ | ✓ | `reservations/views_public.py` (`reserve_action`) |
| **FR09** | ผู้ใช้สามารถระบุจำนวนสินค้าที่ต้องการจองได้ | ✓ | `reservations/forms.py` |
| **FR10** | สร้างรหัสการจอง (Reservation Code) เมื่อจองสำเร็จ | ✓ | `reservations/models.py` (`save` UUID generation) |
| **FR11** | กำหนดเวลาหมดอายุของการจองเป็น 4 ชั่วโมง | ✓ | `reservations/services.py` (`timedelta(hours=4)`) |
| **FR12** | ตรวจสอบสถานะของการจองด้วยรหัสนักศึกษา/รหัสจอง | ✓ | `reservations/views_public.py` (`status_lookup_view`) |
| **FR13** | เปลี่ยนสถานะการจองเป็น Expired เมื่อเกิน 4 ชม. | ✓ | `reservations/services.py` (`expire_overdue_reservations`) |
| **FR14** | คืนจำนวนสินค้าเข้าสู่ Stock เมื่อการจองหมดอายุ | ✓ | `reservations/services.py` |
| **FR15** | Admin สามารถเข้าสู่ระบบได้ | ✓ | `accounts/views.py` (`login_view`) |
| **FR16** | Admin เพิ่มข้อมูลสินค้าได้ | ✓ | `shop/views_manage.py` (`product_create_manage`) |
| **FR17** | Admin แก้ไขข้อมูลสินค้าได้ | ✓ | `shop/views_manage.py` (`product_edit_manage`) |
| **FR18** | Admin ลบข้อมูลสินค้าได้ | ✓ | `shop/views_manage.py` (`product_delete_manage`) |
| **FR19** | Admin เพิ่ม แก้ไข ลบหมวดหมู่สินค้าได้ | ✓ | `shop/views_manage.py` (`category_*`) |
| **FR20** | Admin เพิ่ม แก้ไข ลบจุดจำหน่ายได้ | ✓ | `shop/views_manage.py` (`location_*`) |
| **FR21** | Admin จัดการจำนวน Stock สินค้าในแต่ละสถานที่ได้ | ✓ | `shop/views_manage.py` (`stock_*`) |
| **FR22** | Admin ดูรายการจองทั้งหมดได้ | ✓ | `reservations/views_manage.py` |
| **FR23** | Admin เปลี่ยนสถานะการจองได้ | ✓ | `reservations/views_manage.py` |
| **FR24** | ระบบตรวจสอบสิทธิ์และบทบาท (RBAC) ก่อนอนุญาต | ✓ | `accounts/permissions.py` (`role_required`) |
| **FR25** | Admin เพิ่ม แก้ไข ลบข้อมูล Staff ได้ | ✓ | `accounts/views.py` (`staff_*`) |
| **FR26** | Admin กำหนดสถานที่ที่ Staff รับผิดชอบได้ | ✓ | `accounts/forms.py` (`StaffForm`) |
| **FR27** | Staff สามารถเข้าสู่ระบบได้ | ✓ | `accounts/views.py` (`login_view`) |
| **FR28** | Staff จัดการ Stock ในสถานที่ของตนเองได้ | ✓ | `shop/views_manage.py` |
| **FR29** | Staff ดูรายการจองเฉพาะสถานที่ที่ตนเองรับผิดชอบ | ✓ | `reservations/views_manage.py` |
| **FR30** | Staff เปลี่ยนสถานะการจองของสถานที่ตนเองได้ | ✓ | `reservations/views_manage.py` |
| **FR31** | Staff ดู Dashboard ของสาขาตนเอง (Admin ดูได้ทุกที่) | ✓ | `shop/views_manage.py` (`dashboard_view`) |
| **FR32** | จำกัดสิทธิ์จัดการ Stock ของ Staff เฉพาะสาขาที่สังกัด | ✓ | `shop/forms.py` & `accounts/permissions.py` |
| **FR33** | Admin และ Staff ค้นหาสินค้าจากชื่อได้ | ✓ | `shop/views_manage.py` |
| **FR34** | ป้องกันการเพิ่มข้อมูลสินค้าชื่อซ้ำ | ✓ | `shop/models.py` (`unique=True`) & forms clean |

---

## 6. เวิร์กโฟลว์หลักของระบบ (Main Workflows)

### Workflow 1: การค้นหาและจองสินค้า (Customer)
1. เข้าสู่หน้าแรก หรือ หน้ารายการสินค้า
2. ค้นหาชื่อสินค้า หรือเลือกตามหมวดหมู่
3. ดูรายละเอียดสินค้า และตรวจสอบสต็อกของแต่ละจุดจำหน่าย
4. เลือกร้าน/อาคารที่สะดวกไปรับ กรอกรหัสนักศึกษา ระบุจำนวน และกดยืนยันการจอง
5. ระบบเริ่ม **Atomic Transaction** ตรวจสอบสต็อก ตัดสต็อกทันที และสร้างรหัสจองที่มีอายุ 4 ชั่วโมง
6. แสดงสลิปการจองพร้อมเวลานับถอยหลัง (Countdown Timer)

### Workflow 2: การรับสินค้าที่หน้าร้าน (Counter Pickup)
1. นักศึกษานำรหัสการจอง หรือรหัสนักศึกษา ไปยื่นที่จุดจำหน่ายที่เลือกไว้
2. เจ้าหน้าที่ (Staff) ค้นหารายการในระบบหลังบ้าน
3. ตรวจสอบความถูกต้องและเก็บเงินค่าสินค้า (เงินสดหรือ QR)
4. เจ้าหน้าที่กดปุ่ม **"รับของแล้ว (Pick Up)"**
5. สถานะเปลี่ยนเป็น `picked_up` และบันทึกเวลาจริง

### Workflow 3: การหมดอายุของการจอง (Auto-Expiration)
1. เมื่อการจองมีอายุเกิน 4 ชั่วโมง และยังไม่ได้มารับของ
2. เมื่อระบบมีการเรียกดูรายการ หรือรันฟังก์ชัน `expire_overdue_reservations()`
3. รายการจะถูกปรับสถานะเป็น `expired` โดยอัตโนมัติ
4. สินค้าจะถูกคืนเข้าสู่สต็อกของสาขานั้นในทันที

---

## 7. ข้อมูลบัญชีผู้ใช้สำหรับทดสอบ (Demo Accounts)

ระบบมีข้อมูลจำลองติดตั้งไว้แล้ว สามารถเข้าสู่ระบบได้ที่ `/manage/login/`:

| บทบาท (Role) | Username | Password | สิทธิ์และหน้าที่ |
|---|---|---|---|
| **ผู้ดูแลระบบกลาง (Admin)** | `admin` | `admin1234` | จัดการได้ทุกสาขา, สร้างสินค้า, จัดการ Staff, ดู Dashboard รวม |
| **เจ้าหน้าที่สวัสดิการกลาง** | `staff_welfare` | `staff1234` | จัดการสต็อกและรายการจองเฉพาะ **ร้านสวัสดิการกลาง (อาคาร 40)** |
| **เจ้าหน้าที่คณะวิศวกรรมศาสตร์** | `staff_eng` | `staff1234` | จัดการสต็อกและรายการจองเฉพาะ **จุดจำหน่ายวิศวะ (อาคาร 81)** |

---

## 8. วิธีการรันโปรเจกต์และทดสอบ (Execution Guide)

### ขั้นตอนที่ 1: ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### ขั้นตอนที่ 2: รัน Migration และนำเข้าข้อมูลตัวอย่าง
```bash
python manage.py migrate
python manage.py seed_data
```

### ขั้นตอนที่ 3: เริ่มต้น Local Server
```bash
python manage.py runserver
```
เปิดใช้งานผ่านเบราว์เซอร์:
- **หน้าบ้าน (นักศึกษา):** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **หลังบ้าน (จัดการ/Staff):** [http://127.0.0.1:8000/manage/](http://127.0.0.1:8000/manage/)
- **รายงานผลการทดสอบ (.html):** [http://127.0.0.1:8000/manage/docs/test-report/](http://127.0.0.1:8000/manage/docs/test-report/) หรือเปิดไฟล์ `test_report.html`

### ขั้นตอนที่ 4: การรันชุดทดสอบอัตโนมัติ (Automated Unit Tests)
```bash
python manage.py test
```
ผลลัพธ์: ผ่านครบ 11/11 การทดสอบ (`Ran 11 tests ... OK`).
