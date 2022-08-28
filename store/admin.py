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
    Order
    )



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
    list_display = ("id", "name", "slug", "category", "status")
admin.site.register(Product, ProductAdmin)


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image_tag","color_bg", "size", "price")
admin.site.register(ProductAttribute, ProductAttributeAdmin)


class VATAdmin(admin.ModelAdmin):
    list_display = ("id", "vat")
admin.site.register(VAT, VATAdmin)

class AppUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "address", "joined",)
admin.site.register(AppUser, AppUserAdmin)


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "fk", "p_id", "name", "image_tag", "size", "color", "qty", "price")
admin.site.register(Cart, CartAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "fk", "p_id", "name", "image_tag", "size", "color", "qty", "price")
admin.site.register(Order, OrderAdmin)

# admin.site.unregister(Group)



