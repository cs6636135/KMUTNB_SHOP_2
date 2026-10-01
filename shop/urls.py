from django.urls import path
from . import views_public

app_name = 'shop'

urlpatterns = [
    path('', views_public.home_view, name='home'),
    path('products/', views_public.products_view, name='product_list'),
    path('products/<int:product_id>/', views_public.product_detail_view, name='product_detail'),
]
