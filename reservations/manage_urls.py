from django.urls import path
from . import views_manage

app_name = 'reservations_manage'

urlpatterns = [
    path('reservations/', views_manage.reservations_list_manage, name='reservation_list'),
    path('reservations/<int:reservation_id>/pickup/', views_manage.mark_pickup_manage, name='mark_pickup'),
    path('reservations/<int:reservation_id>/cancel/', views_manage.cancel_reservation_manage, name='cancel_reservation'),
]
