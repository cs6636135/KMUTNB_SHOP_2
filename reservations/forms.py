from django import forms
from shop.models import Product, Location

class ReservationForm(forms.Form):
    student_id = forms.CharField(
        label='รหัสนักศึกษา หรือ เบอร์โทรศัพท์',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-sm shadow-sm',
            'placeholder': 'เช่น 6604062630000 หรือ 0812345678',
            'required': 'true'
        })
    )
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    location_id = forms.IntegerField(
        label='เลือกจุดรับสินค้า',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-sm shadow-sm',
            'required': 'true'
        })
    )
    quantity = forms.IntegerField(
        label='จำนวนที่ต้องการจอง',
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-sm shadow-sm',
            'min': '1',
            'value': '1'
        })
    )

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if product:
            self.fields['product_id'].initial = product.id
            # Populate location choices from available stocks
            valid_stocks = product.stocks.filter(stock__gt=0).select_related('location')
            self.fields['location_id'].widget.choices = [
                (s.location.id, f"{s.location.name} (คงเหลือ {s.stock} ชิ้น)")
                for s in valid_stocks
            ]


class LookupForm(forms.Form):
    query = forms.CharField(
        label='ค้นหาด้วยรหัสนักศึกษา หรือ รหัสการจอง',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-5 py-3.5 rounded-2xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition text-slate-800 text-base shadow-sm',
            'placeholder': 'เช่น 660406263... หรือ KMU-1001-XXXX',
            'autocomplete': 'off',
            'required': 'true'
        })
    )
