from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/create/', views.staff_create_view, name='staff_create'),
    path('staff/<int:user_id>/edit/', views.staff_edit_view, name='staff_edit'),
    path('staff/<int:user_id>/delete/', views.staff_delete_view, name='staff_delete'),
]
