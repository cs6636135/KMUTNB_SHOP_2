from django.urls import path
from . import views_public

app_name = 'reservations'

urlpatterns = [
    path('reserve/', views_public.reserve_action, name='reserve_action'),
    path('reserve/success/<str:code>/', views_public.reserve_success, name='reserve_success'),
    path('status/', views_public.status_lookup_view, name='status_lookup'),
]
