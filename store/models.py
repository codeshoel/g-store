from django.conf import settings
from django.db import models
from django.utils.html import mark_safe
from django.contrib.auth.models import AbstractBaseUser
from .custom.appmanager import AppUserManager




class AppUser(AbstractBaseUser):
    username = None
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, unique=True, null=True)
    mobile = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=500, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    joined = models.DateField(auto_now_add=True, null=True)

    objects = AppUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "mobile", "address"]


    def __str__(self) -> str:
        return self.first_name +" "+ self.last_name

    
    def get_short_name(self) -> str:
        return self.first_name[0]+' '+self.last_name[0]


    def has_perm(self, perm, obj=None) -> bool:
        return True

    def has_module_perms(self, app_label) -> bool:
        return True

    @property
    def is_staff(self) -> bool:
        return self.is_admin


class Category(models.Model):
    class Meta:
        verbose_name = "Category"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Meta:
        verbose_name = "Product"
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    desc = models.TextField()
    status = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Color(models.Model):
    class Meta:
        verbose_name = "Color"

    name = models.CharField(max_length=255)
    color_code = models.CharField(max_length=50)

    def color_bg(self):
        return mark_safe("<div style='background-color: %s; width: 50px; height: 10px;'></div>" %(self.color_code))

    def __str__(self):
        return self.name 


class Size(models.Model):
    class Meta:
        verbose_name = "Size"

    name = models.CharField(max_length=255)
    

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    class Meta:
        verbose_name = "Product Attribute"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/", null=True)
    color = models.ForeignKey(Color, null=True, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, null=True, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    


    def color_bg(self):
        return mark_safe("<div style='background-color: %s; width: 50px; height: 10px;'></div>" %(self.color))

    def image_tag(self):
        return mark_safe(f"<img src='{self.image.url}' width='50px' height='50px' />")


    def __str__(self):
        return self.product.name


class VAT(models.Model):
    class Meta:
        verbose_name = "Value added tax"
    
    vat = models.FloatField(default=0.0)

class Cart(models.Model):
    class Meta:
        verbose_name="Cart"

    fk = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    p_id = models.PositiveBigIntegerField(verbose_name="product id")
    name = models.CharField(max_length=150, null=True)
    qty = models.CharField(max_length=150, null=True)
    size = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True)
    price = models.PositiveIntegerField(null=True)
    image = models.ImageField(null=True)

    def __str__(self) -> str:
        return self.name

    def image_tag(self):
        return mark_safe("<img src='%s' width='50px' height='50px' />" %(self.image))



class Order(models.Model):
    class Meta:
        verbose_name = "Oder"

    fk = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    p_id = models.PositiveBigIntegerField(verbose_name="product id")
    name = models.CharField(max_length=150, null=True)
    qty = models.CharField(max_length=150, null=True)
    size = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True)
    price = models.PositiveIntegerField(null=True)
    image = models.ImageField(null=True)


    def __str__(self):
        return self.name


    def image_tag(self):
        return mark_safe("<img src='%s' width='50px' height='50px' />" %(self.image))




