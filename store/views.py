import json
from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags

from .models import AppUser, Product, ProductAttribute, Cart, Order, Category, Carousel
from .forms import AppUserRegistrationForm, AppUserLoginForm

import stripe


def home(request):
    carousels = Carousel.objects.all().order_by("-id")
 
    return render(request, "pages/index.html", {"carousels": carousels})


def product_list(request):
    if request.method == "GET" and request.GET.get("get_product"):
        products = Product.objects.all().order_by('-id')
        categories = Category.objects.all()
        _products = render_to_string("ajax_templates/products.html", {"products": products})
        categories = render_to_string("ajax_templates/categories.html", {"categories": categories})
        return JsonResponse({'products': _products, 'categories': categories}, safe=False)


def filter_product_by_category(request):
    if request.method == "GET":
        categories = request.GET.getlist('category[]')
        
        minPrice = request.GET["minPrice"]
        maxPrice = request.GET["maxPrice"]
       
        allProduct = Product.objects.all().order_by("-id")
        allProduct = Product.objects.filter(productattribute__price__gte=minPrice).distinct()
        allProduct = Product.objects.filter(productattribute__price__lte=maxPrice).distinct()



        if len(categories) > 0:
            allProduct = allProduct.filter(category__name__in=categories).distinct()
        filter_product_template = render_to_string("ajax_templates/products.html", {"products": allProduct})
        return JsonResponse({"filtered_product": filter_product_template})



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


# This function filters product in the database and return 
# products that match user keyword.
def filter_product_by_search(request):
    if request.method == "POST" and request.POST.get('keyword'):
        keyword = request.POST.get('keyword')
        product = Product.objects.all().order_by('-id')

        if len(keyword) > 1:
            searchProduct = product.filter(name__icontains=keyword).distinct() | product.filter(productattribute__color__name__icontains=keyword).distinct()
            if searchProduct.count() > 0:
                t = render_to_string('ajax_templates/products.html', {'products':searchProduct})
                return JsonResponse({'searched_product': t, 'response': 200})
            return JsonResponse({'searched_product': 404})
    return render(request, "pages/index.html", {})


def add_items_to_cart(request):
    cart_items = {} # session initialization
    if request.method == "GET" and request.GET.get('from-product-detail-page'):
        id = request.GET['id']
        name = request.GET['product_name']
        category = request.GET['product_category']
        image = request.GET['product_image']
        color = request.GET['product_color']
        size = request.GET['product_size']
        qty = request.GET['product_qty']
        price = int(request.GET['product_total_price'])

        # add item to cart table in the database
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
                add_new_item = Cart.objects.create(fk=request.user, p_id=id, name=name, category=category, qty=qty, size=size, color=color, price=price, image=image)
                add_new_item.save()
                total_cart_item = Cart.objects.all().count()
                return JsonResponse({'data': 'authenticated', 'total_cart_item': total_cart_item})

        cart_items[str(request.GET['id'])] = {
            'id':request.GET['id'],
            'image': request.GET['product_image'],
            'name': request.GET['product_name'],
            'category': request.GET['product_category'],
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
                add_new_item = Cart.objects.create(fk=request.user, p_id=product.id, name=product.name, category=str(product.category), qty=qty, size=sizes['size__name'], color=colors['color__name'], price=productattribute.price, image=productattribute.image.url)
                add_new_item.save()
                total_cart_item = Cart.objects.all().count()
                return JsonResponse({'data': 'authenticated', 'total_cart_item': total_cart_item})
        else:
            cart_items[str(product.id)] = {
                'id': product.id,
                'image': productattribute.image.url,
                'name': product.name,
                'category': str(product.category),
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

        # The if control flow updates cart items for authenticated user or customer.
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
            # This update cart items for unauthenticated user or customer.
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
            # fetching and displaying cart items from browser session
            try:    
                for _, item in request.session["cart_data_in_session"].items():
                    total_amt += int(item['qty'])*float(item['price'])
                cart_data = request.session['cart_data_in_session'].items()
                t = render_to_string('ajax_templates/cart-list.html', {'cart_data': cart_data, 'total_amt': total_amt})
                return JsonResponse({'data': t})
            except KeyError:
                request.session['cart_data_in_session'] = cart_items
    return render(request, "pages/cart.html", context={})


def total_cart_item(request):
    if request.method == "GET" and request.GET.get("is_authenticated"):
        total_cart_item = Cart.objects.filter(fk=request.user.id).count()
        return JsonResponse({"data": total_cart_item})

    if request.method == "GET" and request.GET.get("un_authenticated"):
        return JsonResponse({"data": len(request.session['cart_data_in_session'])})
    


def login_user(request):
    form = AppUserLoginForm()
    if request.method == "POST":
        email =  request.POST.get('email')
        password = request.POST.get('password')
        if email and password is not None:
            user = authenticate(email=email, password=password)
            if user is not None:
                try:
                    session_cart_items = request.session['cart_data_in_session'].items()
                    if len(session_cart_items) > 0:
                        # This condition automatically save all cart items added to the user browser(session)
                        # into the database(cart items table), i.e if they are items saved in session
                        # they will be saved to the cart table in the database.
                        login(request, user)
                        for _, item in session_cart_items:
                            try:
                                product = Cart.objects.get(p_id=int(item['id']), fk=request.user)
                                if product:
                                    product.qty = int(product.qty) + int(item['qty'])
                                    product.save()
                            except Exception as e:
                                print(e)
                                add_item_to_db_cart = Cart.objects.create(
                                    fk=request.user,
                                    p_id=item['id'],
                                    name=item['name'],
                                    category=item['category'],
                                    qty=item['qty'],
                                    size=item['size'],
                                    color=item['color'],
                                    price=item['price'],
                                    image=item['image']
                                )
                                add_item_to_db_cart.save()
                           
                        request.session['cart_data_in_session'] = {}
                        return JsonResponse({'data': 200})
                    login(request, user)
                    return JsonResponse({'data': 200})

                except Exception as e:
                    print(e)

            return JsonResponse({"data": 300})

        return JsonResponse({"data": 500})
        
    return render(request, 'pages/registration/login.html', {'form':form})


# Send email to new registered user
def mail_new_user(recepient_email, recepient_name, register_user):
    context = {
        'recepient_name': recepient_name,
    }
    html_content = render_to_string("email_templates/registrationEmail.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
            "Appreciation for project review",
            text_content,
            settings.EMAIL_HOST_USER, 
            [recepient_email],
            )
    print("processing..")
    email.attach_alternative(html_content, 'text/html')
    try:
        email.send()
        return True
    except Exception as e:
        print("Network error", e)
        return False


def user_registration(request):
    form = AppUserRegistrationForm()
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        country = request.POST.get('country')
        city = request.POST.get('city')
        address = request.POST.get('address')
        password = request.POST.get('password')

        if fname and lname and email and mobile and country and city and address and password is not None:
            try:
                AppUser.objects.get(email=email)
                # This return a Json response to the ajax api that email is already in use.
                return JsonResponse({"data": 300})
            except AppUser.DoesNotExist:
                try:
                    session_cart_items = request.session['cart_data_in_session'].items()
                    register_user = AppUser.objects.create_user(
                        first_name=fname, 
                        last_name=lname, 
                        email=email, 
                        mobile=mobile,
                        country=country,
                        city=city, 
                        address=address, 
                        password=password
                        )
                    try:
                        mail_sent = mail_new_user(recepient_email=email, recepient_name=fname, register_user=register_user)
                        if mail_sent == True:
                            register_user.save()
                            if register_user is not None:
                                user = authenticate(request, email=email, password=password)
                                if user.is_active:
                                    if len(session_cart_items) > 0:
                                        # This condition automatically save all cart items added to the user browser(session)
                                        # into the database(cart items table), i.e if they are items saved in session
                                        # they will be saved to the cart table in the database.
                                        login(request, user)
                                        for _, item in session_cart_items:
                                            try:
                                                product = Cart.objects.get(p_id=int(item['id']), fk=request.user)
                                                if product:
                                                    product.qty = int(product.qty) + int(item['qty'])
                                                    product.save()
                                            except Exception as e:
                                                print(e)
                                                add_item_to_db_cart = Cart.objects.create(
                                                    fk=request.user,
                                                    p_id=item['id'],
                                                    name=item['name'],
                                                    category=item['category'],
                                                    qty=item['qty'],
                                                    size=item['size'],
                                                    color=item['color'],
                                                    price=item['price'],
                                                    image=item['image']
                                                )
                                                add_item_to_db_cart.save()
                                        request.session['cart_data_in_session'] = {}
                                        return JsonResponse({"data": 200})
                                    else:
                                        login(request, user)
                                        return JsonResponse({"data": 200})
                        return JsonResponse({"data": 503})
                    except Exception:
                        return JsonResponse({"data": 503}) #Service unavailable(Computer may not be connected to the internet).
                except Exception as e:
                    print("System failed sending email", e)
    return render(request, 'pages/registration/signup.html', {"form":form})


# using stripe as payment gateway
@login_required(login_url="login_url")
def charge_user_cart(request):
    if request.method == "POST":
        try:
            stripe.api_key = "sk_test_Up6yIWJ3o1eYyTAEtkqjTIQV"

            # fetch logged in customer data from g-store server(database)
            customer_data = AppUser.objects.get(id=request.user.id)
            amount = int(request.POST['amount']) * 100
            
            customer = stripe.Customer.create(
                description = "Sales from g-store",
                name = customer_data,
                email= customer_data.email,
                phone = customer_data.mobile,
                source = request.POST['stripeToken'],
            )

            charge = stripe.Charge.create(
                customer = customer,
                amount = amount,
                currency = "usd",
                description = "G-store order",
            )
            if charge.create:
                # Iterate over all customer's purchased product
                # and add/or move them to customer order table according to
                # control flow statements.
                cart_items = Cart.objects.filter(fk=request.user)
                for item in cart_items:

                    # This code filter product by id, iterate over all valide product id matching
                    # a product and make update to that product stock value by subtracting the total quatity(qty)
                    # of the product purchased by the customer from the initial stock value of each of the product.
                    products = Product.objects.filter(id=item.p_id) 
                    for product in products:
                        product.stock = int(product.stock) - int(item.qty)
                    product.save()

                    existing_order = Order.objects.filter(fk=request.user, p_id=item.p_id)
                    # checks if user has pending items already exist in the db order table
                    # if True update exist order by adding new order qty to existing order qty
                    # and then multiply new order price by existing new order qty.
                    # else add new order to existing order 
                    if existing_order.exists():
                        for order in existing_order:
                            order.qty = int(order.qty)+int(item.qty)
                            order.price = int(item.price)*order.qty
                        cart_items = Cart.objects.get(fk=request.user, p_id=order.p_id)
                        cart_items.delete() #Delete successfully purchased items from cart
                        order.save()
                    else:
                        newOrder = Order.objects.create(
                            fk=request.user, 
                            p_id = item.p_id,
                            name=item.name, 
                            qty=item.qty, 
                            size=item.size,
                            color=item.color,
                            price=item.price,
                            image=item.image
                            )
                        cart_items = Cart.objects.get(fk=request.user, p_id=item.p_id)
                        cart_items.delete() #Delete successfully purchased items from cart

                        newOrder.save()
                messages.success(request, "Order was processed successfully...!")
                return redirect("cart_list_url")

        except stripe.error.CardError as e:
            messages.error(request, f"A payment error occurred: {e.user_message}.")
            return redirect("cart_list_url")

        except stripe.error.APIConnectionError:
            messages.error(request, "G-store could not make connection to her payment Gateway.")
            return redirect("cart_list_url")

        except stripe.error.InvalidRequestError:
            # stripe token expired
            #stripe response: You cannot use a Stripe token more than once
            messages.error(request, "Purchase token has expired, please try again.")
            return redirect("cart_list_url")

    return render(request, 'pages/cart.html', {})


def logged_in_user(request):
    return render(request, 'pages/registration/store.html', {})


@login_required(login_url="login_url")
def user_order(request):
    if request.method == "GET" and request.GET.get("customerOrder"):
        orders = Order.objects.filter(fk=request.user).order_by("-id")
        pending_orders = Order.objects.filter(fk=request.user, status=0)
        delivered_orders = Order.objects.filter(fk=request.user, status=1)
        cart_items = Cart.objects.filter(fk=request.user)

        t = render_to_string("ajax_templates/order.html", {"orders": orders})
        context = {
                'order': t, 
                'total_order': orders.count(), 
                'total_item_in_cart': cart_items.count(),
                'total_pending': pending_orders.count(),
                'total_delivered': delivered_orders.count(),
                }
        return JsonResponse(context)
    return render(request, "pages/registration/order.html", {})


@login_required(login_url="login_url")
def delete_order(request):
    if request.method == "GET" and request.GET.get("product_id"):
        product_id = request.GET.get("product_id")
        try:
            order = Order.objects.get(fk=request.user, p_id=product_id)
        except order.DoesNotExist:
            return JsonResponse({"data": 404})
        else:
            order.delete()
            return JsonResponse({"data": 200})
    return render(request, "pages/registration/order.html", {})


@login_required(login_url="login_url")
def log_out_user(request):
    logout(request)
    return redirect('home_url')


@login_required(login_url="login_url")
def user_profile(request):
    user = AppUser.objects.get(id=request.user.id)
    return render(request, "pages/registration/profile.html", {"user": user})


@login_required(login_url="login_url")
def update_user_info(request):
    if request.method == "POST":
        first_name = request.POST.get("fname")
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        country = request.POST.get('country')
        city = request.POST.get('city')
        address = request.POST.get('address')
        try:
            user = AppUser.objects.get(id=request.user.id)
        except user.DoesNotExist:
            return JsonResponse({"data": 404})
        else:
            if first_name and last_name and mobile and country and city and address is not None:
                validate_email = AppUser.objects.filter(email__iexact=email) | AppUser.objects.filter(id=request.user.id, email__iexact=email)
                if validate_email.exists():
                    user.first_name = first_name
                    user.last_name = last_name
                    user.mobile = mobile
                    user.country = country
                    user.city = city
                    user.address = address
                    user.save()
                    return JsonResponse({"email_exist": 200})
                else:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.mobile = mobile
                    user.country = country
                    user.city = city
                    user.address = address
                    user.save()
                    return JsonResponse({"data": 200})
    return render(request, "pages/registration/profile.html", {})


@login_required(login_url="login_url")
def change_password(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        old_password = request.POST.get('old_password')

        user = AppUser.objects.get(id=request.user.id)

        if user.check_password(old_password) == True:
            if user.check_password(new_password) == False:
                # change user password if new password is not the same as existing password.
                user.set_password(new_password)
                user.save()
                return JsonResponse({"data": 200})
            else:
                return JsonResponse({"data": 301}) # return True if new password is same as old password. 
        return JsonResponse({"data": 401})
    return render(request, "pages/registration/profile.html", {})

def error_404_page(request):
    return render(request, "pages/404.html", {})



