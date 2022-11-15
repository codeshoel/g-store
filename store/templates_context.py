from .models import Cart, ProductAttribute
from django.db.models import Min, Max

def context_data(request):
    total_cart_item = Cart.objects.all().count()
    priceRange = ProductAttribute.objects.aggregate(Min('price'), Max('price'))
    context = {
        'total_cart_item': total_cart_item,
        'priceRange': priceRange,
    }
    return context

