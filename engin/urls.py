from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("store.urls")),
    path("store/admin/", include("store_pos.urls")),
    path('admin/', admin.site.urls),
]
