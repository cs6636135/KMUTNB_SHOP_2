from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(
        label='ชื่อผู้ใช้งาน (Username)',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-sm shadow-sm',
            'placeholder': 'เช่น admin หรือ staff_eng',
            'autocomplete': 'username',
            'required': 'true'
        })
    )
    password = forms.CharField(
        label='รหัสผ่าน (Password)',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-sm shadow-sm',
            'placeholder': 'กรอกรหัสผ่านของคุณ',
            'autocomplete': 'current-password',
            'required': 'true'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง')
            if not user.is_active:
                raise forms.ValidationError('บัญชีผู้ใช้นี้ถูกปิดการใช้งาน กรุณาติดต่อผู้ดูแลระบบ')
            cleaned_data['user'] = user
        return cleaned_data


class StaffForm(forms.ModelForm):
    password = forms.CharField(
        label='รหัสผ่าน',
        required=False,
        help_text='(เว้นว่างไว้หากไม่ต้องการเปลี่ยนรหัสผ่านเดิม)',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'location', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'location': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-orange-600 rounded border-gray-300 focus:ring-orange-500'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('ชื่อผู้ใช้งานนี้มีอยู่ในระบบแล้ว')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
