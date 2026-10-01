from django.urls import path
from . import views_manage

app_name = 'shop_manage'

urlpatterns = [
    path('', views_manage.dashboard_view, name='dashboard'),
    
    # Products
    path('products/', views_manage.product_list_manage, name='product_list'),
    path('products/create/', views_manage.product_create_manage, name='product_create'),
    path('products/<int:product_id>/edit/', views_manage.product_edit_manage, name='product_edit'),
    path('products/<int:product_id>/delete/', views_manage.product_delete_manage, name='product_delete'),

    # Categories
    path('categories/', views_manage.category_list_manage, name='category_list'),
    path('categories/create/', views_manage.category_create_manage, name='category_create'),
    path('categories/<int:category_id>/edit/', views_manage.category_edit_manage, name='category_edit'),
    path('categories/<int:category_id>/delete/', views_manage.category_delete_manage, name='category_delete'),

    # Locations
    path('locations/', views_manage.location_list_manage, name='location_list'),
    path('locations/create/', views_manage.location_create_manage, name='location_create'),
    path('locations/<int:location_id>/edit/', views_manage.location_edit_manage, name='location_edit'),
    path('locations/<int:location_id>/delete/', views_manage.location_delete_manage, name='location_delete'),

    # Stock
    path('stock/', views_manage.stock_list_manage, name='stock_list'),
    path('stock/create/', views_manage.stock_create_or_update_manage, name='stock_create'),
    path('stock/<int:stock_id>/inline-update/', views_manage.stock_inline_update, name='stock_inline_update'),

    # Documentation & Test Report (PDF p. 16-17)
    path('docs/test-report/', views_manage.test_report_view, name='test_report'),
]
