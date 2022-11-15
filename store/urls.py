from django.urls import path
from . import views


#imports for media settings
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home_url"),
    path('product-list/', views.product_list, name="products"),
    path('filter-product-by-category/', views.filter_product_by_category, name="fiter_by_category"),
    path('filter-product-by-search/', views.filter_product_by_search, name="filter_product_by_search"),

    path('product-detail/<int:pk>', views.product_details, name="product_detail_url"),
    path('product-detail-filter/', views.product_detail_filter, name="product_detail_url"),

    path('add-items-session-cart', views.add_items_to_session_cart, name="addtosession_url"),
    path('cart-list/', views.cart_list, name='cart_list_url'),
    path('update-cart-item/', views.update_cart_item, name='edit_cart_item_url'),
    path('del-cart-item/', views.delete_cart_item, name="delete_cart_item_url"),


    # path('auth-cart/', views.authenticated_cart_page, name='authenticated_cart_page_url'),
    path('charge/', views.charge_user_cart, name="charge_url"),

    path('404-page/', views.error_404_page, name="404_url"),

    path('user-registration/', views.user_registration, name="user_registration_url"),
    path('login-user/', views.login_user, name="login_url"),
    path('account/', views.logged_in_user, name="store_url"),
    path('orders/', views.user_order, name="order_url"),
    path('delete-order/', views.delete_order, name="order_url"),
    path('user-profile/', views.user_profile, name="user_profile_url"),
    path('update-info/', views.update_user_info, name="update_user_info_url"),
    path('logout/', views.log_out_user, name="logout_url"),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


