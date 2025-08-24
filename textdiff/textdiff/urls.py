from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('comparator.urls')),  # include کردن تمام مسیرهای اپ
]
