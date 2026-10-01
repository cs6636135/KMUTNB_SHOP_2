from django import forms
from .models import Category, Product, Location, Stock

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'ชื่อหมวดหมู่ เช่น เครื่องแบบ, อุปกรณ์การเรียน'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'rows': 3, 'placeholder': 'รายละเอียดหมวดหมู่ (ถ้ามี)'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'image_url', 'reservable']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'เช่น เสื้อช็อป KMUTNB, สมุดโน้ตวิศวะ'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'rows': 4, 'placeholder': 'รายละเอียดสินค้า'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'step': '0.50', 'min': '0'}),
            'image_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'https://...'}),
            'reservable': forms.CheckboxInput(attrs={'class': 'h-5 w-5 text-orange-600 rounded border-gray-300 focus:ring-orange-500'}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('ราคาสินค้าต้องไม่ติดลบ')
        return price


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'building', 'floor', 'room', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'ชื่อจุดจำหน่าย เช่น ร้านค้าสวัสดิการ มจพ.'}),
            'building': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'อาคาร 40 หรือ อาคาร 81'}),
            'floor': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': '1'}),
            'room': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'placeholder': 'ห้องจำหน่ายของที่ระลึก'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'rows': 3}),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['product', 'location', 'stock']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'location': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-sm', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_shop_admin:
            # Staff is constrained to their assigned location only
            if user.location:
                self.fields['location'].queryset = Location.objects.filter(pk=user.location.pk)
                self.fields['location'].initial = user.location
                self.fields['location'].widget.attrs['disabled'] = 'disabled'
            else:
                self.fields['location'].queryset = Location.objects.none()

    def clean_location(self):
        # If disabled in HTML, retrieve from initial or instance
        instance_loc = getattr(self.instance, 'location', None)
        return self.cleaned_data.get('location') or instance_loc
