from email.headerregistry import Group
from django.contrib import admin
from .models import (
    Category, 
    Color, 
    Size, 
    Product, 
    ProductAttribute, 
    VAT, 
    AppUser,
    Cart,
    Order,
    Carousel
    )


class CarouselAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "desc", "image", "interval", "is_active", "created")
admin.site.register(Carousel, CarouselAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
admin.site.register(Category, CategoryAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color_bg")
admin.site.register(Color, ColorAdmin)


class SizeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
admin.site.register(Size, SizeAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "stock", "name", "slug", "category", "status")
admin.site.register(Product, ProductAdmin)


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image_tag","color_bg", "size", "price")
admin.site.register(ProductAttribute, ProductAttributeAdmin)


class VATAdmin(admin.ModelAdmin):
    list_display = ("id", "vat")
admin.site.register(VAT, VATAdmin)

class AppUserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "country", "city", "address", "joined",)
admin.site.register(AppUser, AppUserAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "fk", "p_id", "name", "image_tag", "size", "color", "qty", "price")
admin.site.register(Cart, CartAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "fk", "p_id", "name", "image_tag", "size", "color", "qty", "price", "status", "date")
admin.site.register(Order, OrderAdmin)

# admin.site.unregister(Group)



