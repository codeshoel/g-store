from django.urls import path
from . import views


app_name = "store_admin"

urlpatterns = [
    path("", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("store/customers", views.customers, name="customers"),
    path("store/products", views.store_product, name="store"),
    path("store/orders", views.store_product, name="orders"),
]


