from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from accounts.permissions import admin_required, staff_or_admin_required, limit_to_location
from accounts.models import User
from .models import Category, Product, Location, Stock
from .forms import CategoryForm, ProductForm, LocationForm, StockForm
from reservations.models import Reservation
from reservations.services import expire_overdue_reservations

@staff_or_admin_required
def dashboard_view(request):
    user = request.user
    # Automatically expire any overdue reservations upon viewing dashboard
    expire_overdue_reservations()

    is_admin = user.is_shop_admin
    user_location = user.location

    # Base querysets
    stock_qs = Stock.objects.all()
    res_qs = Reservation.objects.all()

    if not is_admin:
        # Staff is strictly scoped to user_location (FR31)
        stock_qs = stock_qs.filter(location=user_location)
        res_qs = res_qs.filter(location=user_location)

    total_products = Product.objects.count()
    total_locations = Location.objects.count()
    total_units_stock = stock_qs.aggregate(total=Sum('stock'))['total'] or 0

    active_reservations = res_qs.filter(status='reserved').count()
    picked_up_today = res_qs.filter(
        status='picked_up',
        picked_up_at__date=timezone.now().date()
    ).count()
    expired_reservations = res_qs.filter(status='expired').count()

    recent_reservations = res_qs.select_related('product', 'location').order_by('-reserved_at')[:8]
    low_stocks = stock_qs.select_related('product', 'location').filter(stock__lte=5).order_by('stock')[:6]

    locations_summary = []
    if is_admin:
        for loc in Location.objects.all():
            loc_stocks = Stock.objects.filter(location=loc).aggregate(t=Sum('stock'))['t'] or 0
            loc_res = Reservation.objects.filter(location=loc, status='reserved').count()
            locations_summary.append({
                'location': loc,
                'total_stock': loc_stocks,
                'active_reservations': loc_res,
            })

    context = {
        'is_admin': is_admin,
        'user_location': user_location,
        'total_products': total_products,
        'total_locations': total_locations,
        'total_units_stock': total_units_stock,
        'active_reservations': active_reservations,
        'picked_up_today': picked_up_today,
        'expired_reservations': expired_reservations,
        'recent_reservations': recent_reservations,
        'low_stocks': low_stocks,
        'locations_summary': locations_summary,
    }
    return render(request, 'manage/dashboard.html', context)


# ==========================================
# Product Management (Admin Only)
# ==========================================

@admin_required
def product_list_manage(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    products = Product.objects.select_related('category').prefetch_related('stocks__location').all()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(request, 'manage/products.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
    })


@admin_required
def product_create_manage(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            # Check duplicate product name (FR34)
            name = form.cleaned_data['name'].strip()
            if Product.objects.filter(name__iexact=name).exists():
                form.add_error('name', 'มีสินค้านี้อยู่ในระบบแล้ว (ป้องกันการเพิ่มซ้ำ FR34)')
            else:
                product = form.save()
                messages.success(request, f'เพิ่มสินค้า "{product.name}" สำเร็จ')
                return redirect('shop_manage:product_list')
    else:
        form = ProductForm()

    return render(request, 'manage/product_form.html', {
        'form': form,
        'title': 'เพิ่มข้อมูลสินค้าใหม่',
        'is_edit': False,
    })


@admin_required
def product_edit_manage(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            if Product.objects.filter(name__iexact=name).exclude(id=product.id).exists():
                form.add_error('name', 'มีสินค้านี้อยู่ในระบบแล้ว (ป้องกันการเพิ่มซ้ำ FR34)')
            else:
                form.save()
                messages.success(request, f'บันทึกข้อมูลสินค้า "{product.name}" สำเร็จ')
                return redirect('shop_manage:product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'manage/product_form.html', {
        'form': form,
        'title': f'แก้ไขสินค้า: {product.name}',
        'is_edit': True,
        'product': product,
    })


@admin_required
@require_http_methods(['POST'])
def product_delete_manage(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    name = product.name
    product.delete()
    messages.success(request, f'ลบสินค้า "{name}" สำเร็จ')
    return redirect('shop_manage:product_list')


# ==========================================
# Category Management (Admin Only)
# ==========================================

@admin_required
def category_list_manage(request):
    categories = Category.objects.annotate(product_count=Count('products')).all()
    form = CategoryForm()
    return render(request, 'manage/categories.html', {
        'categories': categories,
        'form': form,
    })


@admin_required
def category_create_manage(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'เพิ่มหมวดหมู่ "{cat.name}" สำเร็จ')
            return redirect('shop_manage:category_list')
    else:
        form = CategoryForm()

    return render(request, 'manage/category_form.html', {
        'form': form,
        'title': 'เพิ่มหมวดหมู่สินค้า',
        'is_edit': False,
    })


@admin_required
def category_edit_manage(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขหมวดหมู่ "{category.name}" สำเร็จ')
            return redirect('shop_manage:category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'manage/category_form.html', {
        'form': form,
        'title': f'แก้ไขหมวดหมู่: {category.name}',
        'is_edit': True,
        'category': category,
    })


@admin_required
@require_http_methods(['POST'])
def category_delete_manage(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    name = category.name
    category.delete()
    messages.success(request, f'ลบหมวดหมู่ "{name}" สำเร็จ')
    return redirect('shop_manage:category_list')


# ==========================================
# Location Management (Admin Only)
# ==========================================

@admin_required
def location_list_manage(request):
    locations = Location.objects.annotate(
        stock_count=Count('stocks'),
        res_count=Count('reservations')
    ).all()
    return render(request, 'manage/locations.html', {
        'locations': locations,
    })


@admin_required
def location_create_manage(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            loc = form.save()
            messages.success(request, f'เพิ่มจุดจำหน่าย "{loc.name}" สำเร็จ')
            return redirect('shop_manage:location_list')
    else:
        form = LocationForm()

    return render(request, 'manage/location_form.html', {
        'form': form,
        'title': 'เพิ่มจุดจำหน่ายสินค้า / สาขา',
        'is_edit': False,
    })


@admin_required
def location_edit_manage(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขจุดจำหน่าย "{location.name}" สำเร็จ')
            return redirect('shop_manage:location_list')
    else:
        form = LocationForm(instance=location)

    return render(request, 'manage/location_form.html', {
        'form': form,
        'title': f'แก้ไขจุดจำหน่าย: {location.name}',
        'is_edit': True,
        'location': location,
    })


@admin_required
@require_http_methods(['POST'])
def location_delete_manage(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    name = location.name
    location.delete()
    messages.success(request, f'ลบจุดจำหน่าย "{name}" สำเร็จ')
    return redirect('shop_manage:location_list')


# ==========================================
# Stock Management (FR21, FR28, FR32)
# ==========================================

@staff_or_admin_required
def stock_list_manage(request):
    user = request.user
    is_admin = user.is_shop_admin
    selected_loc_id = request.GET.get('location', '').strip()
    search_q = request.GET.get('q', '').strip()

    stocks = Stock.objects.select_related('product', 'location', 'product__category')

    if is_admin:
        locations = Location.objects.all()
        if selected_loc_id:
            stocks = stocks.filter(location_id=selected_loc_id)
    else:
        # Staff is strictly limited to their location (FR32)
        locations = Location.objects.filter(pk=user.location_id) if user.location else Location.objects.none()
        stocks = stocks.filter(location=user.location)

    if search_q:
        stocks = stocks.filter(product__name__icontains=search_q)

    return render(request, 'manage/stock.html', {
        'stocks': stocks,
        'locations': locations,
        'is_admin': is_admin,
        'selected_location': selected_loc_id,
        'search_q': search_q,
        'user_location': user.location,
    })


@staff_or_admin_required
def stock_create_or_update_manage(request):
    user = request.user
    is_admin = user.is_shop_admin

    if request.method == 'POST':
        stock_id = request.POST.get('stock_id')
        product_id = request.POST.get('product')
        stock_qty = request.POST.get('stock', 0)

        # Determine location
        if is_admin:
            location_id = request.POST.get('location')
        else:
            if not user.location:
                messages.error(request, 'คุณยังไม่ได้รับการกำหนดสาขาประจำการ กรุณาแจ้ง Admin')
                return redirect('shop_manage:stock_list')
            location_id = user.location.id

        try:
            qty = int(stock_qty)
            if qty < 0:
                raise ValueError("จำนวนสต็อกต้องไม่ติดลบ")
        except ValueError:
            messages.error(request, 'กรุณาระบุจำนวนสต็อกเป็นตัวเลขที่ถูกต้องและไม่ติดลบ')
            return redirect('shop_manage:stock_list')

        location_obj = get_object_or_404(Location, id=location_id)
        product_obj = get_object_or_404(Product, id=product_id)

        # Update or create stock entry
        stock_obj, created = Stock.objects.update_or_create(
            product=product_obj,
            location=location_obj,
            defaults={'stock': qty}
        )

        action_str = 'เพิ่มสินค้าเข้าสต็อก' if created else 'ปรับปรุงจำนวนสต็อก'
        messages.success(request, f'{action_str} "{product_obj.name}" ที่สาขา "{location_obj.name}" เป็น {qty} ชิ้น เรียบร้อย')
        return redirect('shop_manage:stock_list')

    # GET request
    products = Product.objects.all()
    if is_admin:
        locations = Location.objects.all()
    else:
        locations = Location.objects.filter(pk=user.location_id) if user.location else Location.objects.none()

    return render(request, 'manage/stock_form.html', {
        'products': products,
        'locations': locations,
        'is_admin': is_admin,
        'user_location': user.location,
    })


@staff_or_admin_required
@require_http_methods(['POST'])
def stock_inline_update(request, stock_id):
    """
    HTMX or direct POST to quickly update stock level
    """
    stock_obj = get_object_or_404(Stock, id=stock_id)
    user = request.user

    # Security check: if Staff, verify ownership
    if not user.is_shop_admin and stock_obj.location != user.location:
        messages.error(request, 'คุณไม่มีสิทธิ์แก้ไขสต็อกของสาขาอื่น')
        return redirect('shop_manage:stock_list')

    try:
        new_qty = int(request.POST.get('stock', stock_obj.stock))
        if new_qty < 0:
            raise ValueError()
        stock_obj.stock = new_qty
        stock_obj.save()
        messages.success(request, f'อัปเดตสต็อก "{stock_obj.product.name}" สำเร็จ ({new_qty} ชิ้น)')
    except ValueError:
        messages.error(request, 'จำนวนสต็อกไม่ถูกต้อง')

    return redirect('shop_manage:stock_list')


def test_report_view(request):
    """
    Displays the automated Test & Evaluation Report (PDF pages 16-17)
    """
    return render(request, 'test_report.html', {})

