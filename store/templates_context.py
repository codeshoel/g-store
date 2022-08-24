from .models import Cart

def context_data(request):
    total_cart_item = Cart.objects.all().count()
    context = {
        'total_cart_item': total_cart_item
    }
    return context

