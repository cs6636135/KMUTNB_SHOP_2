from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, StaffForm
from .permissions import admin_required
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop_manage:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f'ยินดีต้อนรับคุณ {user.get_full_name() or user.username} เข้าสู่ระบบ')
            next_url = request.GET.get('next') or 'shop_manage:dashboard'
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'manage/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('accounts:login')


@admin_required
def staff_list_view(request):
    staff_members = User.objects.select_related('location').all().order_by('-date_joined')
    return render(request, 'manage/staff.html', {
        'staff_members': staff_members,
    })


@admin_required
def staff_create_view(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'สร้างบัญชีเจ้าหน้าที่ {user.username} เรียบร้อยแล้ว')
            return redirect('accounts:staff_list')
    else:
        form = StaffForm()

    return render(request, 'manage/staff_form.html', {
        'form': form,
        'title': 'เพิ่มบัญชีผู้ใช้งาน / เจ้าหน้าที่',
        'is_edit': False,
    })


@admin_required
def staff_edit_view(request, user_id):
    staff_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff_user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'แก้ไขข้อมูลผู้ใช้ {user.username} สำเร็จ')
            return redirect('accounts:staff_list')
    else:
        form = StaffForm(instance=staff_user)

    return render(request, 'manage/staff_form.html', {
        'form': form,
        'title': f'แก้ไขบัญชี: {staff_user.username}',
        'is_edit': True,
        'staff_user': staff_user,
    })


@admin_required
@require_http_methods(['POST'])
def staff_delete_view(request, user_id):
    staff_user = get_object_or_404(User, id=user_id)
    if staff_user == request.user:
        messages.error(request, 'ไม่สามารถลบบัญชีของตนเองที่กำลังเข้าสู่ระบบอยู่ได้')
    else:
        username = staff_user.username
        staff_user.delete()
        messages.success(request, f'ลบบัญชีผู้ใช้ {username} สำเร็จ')
    return redirect('accounts:staff_list')
