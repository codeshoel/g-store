import uuid
from django.shortcuts import redirect, render, HttpResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login, logout

from .models import AppUser, Product, ProductAttribute, Cart
from .forms import AppUserRegistrationForm, AppUserLoginForm






def home(request):
    return render(request, "pages/index.html", {})


def product_list(request):
    if request.method == "GET" and request.GET.get("get_product"):
        products = Product.objects.all().order_by('-id')
        t = render_to_string("ajax_templates/products.html", {"products": products})
        return JsonResponse({'data': t}, safe=False)


def product_details(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        relate_product = Product.objects.filter(category=product.category).exclude(pk=product.id)

        colors = ProductAttribute.objects.filter(product=product).values("color__id", "color__name", "color__color_code").distinct()
        # sizes = ProductAttribute.objects.filter(product=product).values("size__name", "size__id", "color__id").distinct()
        context = {
            "product_detail": product, 
            "relate_products": relate_product,
            "colors": colors,
            # "sizes": sizes,
        }
    except Product.DoesNotExist:
        return redirect('404_url')
    
    return render(request, "pages/product-detail.html", context)


def product_detail_filter(request):
    
    if request.method == 'GET' and request.GET.get('color_id'):
        try:
            product_id = request.GET.get('product_id')
            color_id = request.GET.get('color_id')

            if product_id and color_id is not None:
                size = ProductAttribute.objects.filter(color=color_id, product=product_id).values("size__name", "price", "product", "color__name")
                t = render_to_string('ajax_templates/size-button.html', {'sizes':size})
                return JsonResponse({'data': t})
        except ProductAttribute.DoesNotExist:
            return JsonResponse({'data': 404})

        except ValueError:
            return JsonResponse({'data': 502}) #bad Gateway

    return render(request, "pages/product-detail.html", {})



def add_items_to_session_cart(request):
    cart_items = {}
    if request.method == "GET" and request.GET.get('from-product-detail-page'):
        id = request.GET['id']
        name = request.GET['product_name']
        image = request.GET['product_image']
        color = request.GET['product_color']
        size = request.GET['product_size']
        qty = request.GET['product_qty']
        price = int(request.GET['product_total_price'])

        if request.user.is_authenticated:
            try:
                cart = Cart.objects.get(p_id=id)
                new_qty = int(cart.qty) +1
                cart.size = size
                cart.color = color
                cart.qty = new_qty
                cart.price = price
                cart.save()
            except Cart.DoesNotExist:
                add_new_item = Cart.objects.create(fk=request.user, p_id=id, name=name, qty=qty, size=size, color=color, price=price, image=image)
                add_new_item.save()
                total_cart_item = Cart.objects.all().count()
                return JsonResponse({'data': 'authenticated', 'total_cart_item': total_cart_item})

        cart_items[str(request.GET['id'])] = {
            'id':request.GET['id'],
            'image': request.GET['product_image'],
            'name': request.GET['product_name'],
            'slug': request.GET['product_slug'],
            'color': request.GET['product_color'],
            'size': request.GET['product_size'],
            'qty': request.GET['product_qty'],
            'price': int(request.GET['product_total_price']),
        }
        # adding product or item from product detail page
        if 'cart_data_in_session' in request.session:
            if str(request.GET['id']) in request.session['cart_data_in_session']:
                cart_data = request.session['cart_data_in_session']
                cart_data[str(request.GET['id'])]['qty'] = int(cart_data[str(request.GET['id'])]['qty'])
                cart_data.update(cart_items)
                request.session['cart_data_in_session'] = cart_data
            else:
                cart_data = request.session['cart_data_in_session']
                cart_data.update(cart_items)
                request.session['cart_data_in_session'] = cart_data
        else:
            request.session['cart_data_in_session'] = cart_items
    
    # adding product or item from product page
    if request.method == "GET" and request.GET.get('home-page'):
        id = request.GET.get('id')
        qty = 1
        product = Product.objects.get(id=id)
        productattribute = ProductAttribute.objects.filter(product=product).first()
        colors = ProductAttribute.objects.filter(product=product).values('color__name').first()
        sizes = ProductAttribute.objects.filter(product=product).values('size__name').first()

        if request.user.is_authenticated:
            try:
                cart = Cart.objects.get(p_id=product.id)
                new_qty = int(cart.qty) +1
                cart.qty = new_qty
                cart.save()
            except Cart.DoesNotExist:
                add_new_item = Cart.objects.create(fk=request.user, p_id=product.id, name=product.name, qty=qty, size=sizes['size__name'], color=colors['color__name'], price=productattribute.price, image=productattribute.image.url)
                add_new_item.save()
                total_cart_item = Cart.objects.all().count()
                return JsonResponse({'data': 'authenticated', 'total_cart_item': total_cart_item})
        else:
            cart_items[str(product.id)] = {
                'id': product.id,
                'image': productattribute.image.url,
                'name': product.name,
                'slug': product.slug,
                'color': colors['color__name'],
                'size': sizes['size__name'],
                'qty': qty,
                'price': int(productattribute.price),
            }
            if 'cart_data_in_session' in request.session:
                #update product or item if in cart
                if id in request.session['cart_data_in_session']:
                    _qty = request.session['cart_data_in_session'][str(request.GET['id'])]['qty']
                    _qty = int(_qty) +1
                    cart_data = request.session['cart_data_in_session']
                    cart_data[str(request.GET['id'])]['qty'] = _qty
                    request.session['cart_data_in_session'] = cart_data
                    return JsonResponse({'data': "unauthenticated", 'total_cart_item_in_session': len(request.session['cart_data_in_session'])})
            
                #add product or item if not in cart
                if id not in request.session['cart_data_in_session']:
                    cart_data = request.session['cart_data_in_session']
                    cart_data.update(cart_items)
                    request.session['cart_data_in_session'] = cart_data
                    return JsonResponse({'data': "unauthenticated", 'total_cart_item_in_session': len(request.session['cart_data_in_session'])})
            else:        
                request.session['cart_data_in_session'] = cart_items
                return JsonResponse({'data': "unauthenticated", 'total_cart_item_in_session': len(request.session['cart_data_in_session'])})
    return JsonResponse({'data': ''}) #created
    

def update_cart_item(request):
    if request.method == "GET":
        product_id = str(request.GET['id'])
        qty = request.GET['qty']
        total_amt = 0
        priceList = []

        if request.user.is_authenticated:
            cart_data_ = Cart.objects.get(fk=request.user, p_id=int(product_id))
            new_qty = int(qty)
            cart_data_.qty = new_qty
            cart_data_.save()

            cart_data = Cart.objects.filter(fk=request.user).order_by('-id')
            for item in cart_data:
                sub_total = int(item.qty) * item.price
                priceList.append(sub_total)
            total_amt = sum(priceList)

            context = {
                'cart_data': cart_data, 
                'total_amt': total_amt, 
                'total_cart_item': cart_data.count(),
                }
            t = render_to_string('ajax_templates/auth-cart.html', context)
            return JsonResponse({'data': t})    
        else:
            if 'cart_data_in_session' in request.session:
                if product_id in request.session['cart_data_in_session']:
                    cart_data = request.session['cart_data_in_session']
                    cart_data[str(request.GET['id'])]['qty'] = qty
                    request.session['cart_data_in_session'] = cart_data
    
            if 'cart_data_in_session' in request.session:
                for _, item in request.session["cart_data_in_session"].items():
                    total_amt += int(item['qty'])*float(item['price'])
                
                cart_data = request.session['cart_data_in_session'].items()

                t = render_to_string('ajax_templates/cart-list.html', {'cart_data': cart_data, 'total_amt': total_amt})
                return JsonResponse({'data': t})
    return render(request, "pages/cart.html", context={})


def delete_cart_item(request):
    if request.method == "GET" and request.GET.get("del-cart-item"):
        id = request.GET.get('id')
        if request.user.is_authenticated:
            cart_item = Cart.objects.get(fk=request.user, p_id=int(id))
            cart_item.delete()
            return JsonResponse({"data": 200})
        else:
            if 'cart_data_in_session' in request.session:
                if id in request.session['cart_data_in_session']:
                    del request.session['cart_data_in_session'][id]
                    request.session.modified = True #this code tells Python to update the session due to changes that was done
                    return JsonResponse({"data": 200})
                return JsonResponse({'data': 300})
    return render(request, "pages/cart.html", context={})


def cart_list(request):
    total_amt = 0
    cart_items = {}
    priceList = []
    if request.method == "GET" and request.GET.get("getCartItemList"):
        if request.user.is_authenticated:
            # fetching and displaying cart items for authenticated user from the database
            cart_data = Cart.objects.filter(fk=request.user).order_by('-id')
            for item in cart_data:
                sub_total = int(item.qty) * item.price
                priceList.append(sub_total)
            total_amt = sum(priceList)
            context = {
                'cart_data': cart_data, 
                'total_amt': total_amt,
                'total_cart_item': cart_data.count(),
            }
            t = render_to_string("ajax_templates/auth-cart.html", context)
            return JsonResponse({'data': t})
        else:
            # # fetching and displaying cart items from browser catch session
            # if 'cart_data_in_session' in request.session:
            #     for _, item in request.session["cart_data_in_session"].items():
            #         total_amt += int(item['qty'])*float(item['price'])
            try:    
                for _, item in request.session["cart_data_in_session"].items():
                    total_amt += int(item['qty'])*float(item['price'])
                
                cart_data = request.session['cart_data_in_session'].items()
                

                t = render_to_string('ajax_templates/cart-list.html', {'cart_data': cart_data, 'total_amt': total_amt})
                return JsonResponse({'data': t})
            except KeyError:
                request.session['cart_data_in_session'] = cart_items

    return render(request, "pages/cart.html", context={})
    


def authenticated_cart_page(request):
    cart = Cart.objects.filter(fk=request.user)
    return render(request, 'pages/cart.html', {"cart": cart})



def login_user(request):
    form = AppUserLoginForm()
    if request.method == "POST":
        email =  request.POST.get('email')
        password = request.POST.get('password')
        if email and password is not None:
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'data': 200})
            return JsonResponse({"data": 300})
        return JsonResponse({"data": 500})
    return render(request, 'pages/registration/login.html', {'form':form})

def user_registration(request):
    form = AppUserRegistrationForm()
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        password = request.POST.get('password')

        if fname and lname and email and mobile and address and password is not None:
            try:
                AppUser.objects.get(email=email)
                return JsonResponse({"data": 300})

            except AppUser.DoesNotExist:
                try:
                    session_cart_items = request.session['cart_data_in_session'].items()
                    register_user = AppUser.objects.create_user(
                        first_name=fname, 
                        last_name=lname, 
                        email=email, 
                        mobile=mobile, 
                        address=address, 
                        password=password
                        )
                    register_user.save()
                    if register_user is not None:
                        user = authenticate(request, email=email, password=password)
                        if user.is_active:
                            login(request, user)
                            for _, item in session_cart_items:
                                add_item_to_db_cart = Cart.objects.create(
                                    fk=request.user,
                                    name=item['name'],
                                    qty=item['qty'],
                                    size=item['size'],
                                    color=item['color'],
                                    price=item['price'],
                                    image=item['image']
                                )
                            add_item_to_db_cart.save()
                            request.session['cart_data_in_session'] = {}
                            return JsonResponse({"data": 200})
                except KeyError:
                    pass

    return render(request, 'pages/registration/signup.html', {"form":form})


def charge_user_cart(request):
    amount = 5
    if request.method == "POST":
        print('Data:', request.POST)
    return render(request, 'pages/cart.html', {})




def logged_in_user(request):
    return render(request, 'pages/registration/profile.html', {})

def log_out_user(request):
    logout(request)
    return redirect('home_url')


def error_404_page(request):
    return render(request, "pages/404.html", {})




