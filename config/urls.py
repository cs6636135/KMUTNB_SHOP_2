from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Built-in Admin
    path('admin/', admin.site.urls),

    # Accounts & Authentication
    path('manage/', include('accounts.urls')),

    # Backoffice / Admin / Staff Management (/manage/...)
    path('manage/', include('shop.manage_urls')),
    path('manage/', include('reservations.manage_urls')),

    # Public Shop Front (/...)
    path('', include('shop.urls')),
    path('', include('reservations.urls')),
]
