from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
import random
from django.urls import reverse
from datetime import datetime, timedelta
from .models import *
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .vectorize import vectorize_product_with_reviews,vectorize_user_with_search,pd
from django.shortcuts import render
from .models import *
from .read_content import *
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sentence_transformers import SentenceTransformer
from django.db.models import Case, When
import numpy as np
import torch






def getuser(request):
    return request.session.get('user')


# def filter_price(data, price):
#     price2 = []
#     for i in data:
#         for j in price:
#             if i.pk == j.product.pk:
#                 price2.append(j)
#                 break
#     return price2


def types(request):
    type2 = []
    for i in Gallery.objects.all():
        if i.name and i.model not in type2:
            type2.append(i.model)
    return type2


def index(request):
    if request.method == 'POST' and 'image' in request.FILES:  
        myimage = request.FILES['image']
        image1 = request.FILES['image1']
        image2 = request.FILES['image2']
        image3 = request.FILES['image3']  
        name = request.POST.get("todo")
        discription = request.POST.get("description")
        price = request.POST.get("date")
        quanty = request.POST.get("quant")
        mod = request.POST.get("model")
        off = request.POST.get("offers")
        obj = Gallery(
            name=name,
            price=price,
            model=mod,
            quantity=quanty,
            offers=off,
            discription=discription,
            feedimage=myimage,
            image2=image2,
            image3=image3,
            user=request.user
        )
        obj.save()
        pro_data = [{
            "pro_id": obj.id,
            "name": name,
            "rating": 0,
            "description": discription,
            "reviews": '',
            "model": model # Add the model key here
        }]
        df = pd.DataFrame(pro_data)
        product_vector = vectorize_product_with_reviews(df)
        print('pro', product_vector)
        obj.vector_data = json.dumps(product_vector[0].tolist())
        obj.save()
        return redirect('adminpage')
    return render(request, 'main/index.html')
    
def verifyotp(request):
    if request.POST:
        otp = request.POST.get('otp')
        otp1 = request.session.get('otp')
        otp_time_str = request.session.get('otp_time')
        if otp_time_str:
            otp_time = datetime.fromisoformat(otp_time_str)  
            otp_expiry_time = otp_time + timedelta(minutes=5)
            if datetime.now() > otp_expiry_time:
                messages.error(request, 'OTP has expired. Please request a new one.')
                del request.session['otp']
                del request.session['otp_time']
                return redirect('verifyotp')
        if otp == otp1:
            del request.session['otp']
            del request.session['otp_time']
            return redirect('passwordreset')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    otp = ''.join(random.choices('123456789', k=6))
    request.session['otp'] = otp
    request.session['otp_time'] = datetime.now().isoformat()
    message = f'Your email verification code is: {otp}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.session.get('email')]
    send_mail('Email Verification', message, email_from, recipient_list)

    return render(request, "otp.html")

def getusername(request):
    if request.POST:
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            request.session['email'] = user.email
            return redirect('verifyotp')
        except User.DoesNotExist:
            messages.error(request, "Username does not exist.")
            return redirect('getusername')

    return render(request, 'getusername.html')

def passwordreset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')
        if confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        else:
            email = request.session.get('email')
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                del request.session['email']
                messages.success(request, "Your password has been reset successfully.")
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)

                return redirect('sellerlogin')
            except User.DoesNotExist:
                messages.error(request, "No user found with that email address.")
                return redirect('getusername')

    return render(request, "passwordreset.html")
# def firstpage(request):
#     gallery_images = Gallery.objects.all()
#     return render(request, "firstpage.html", {"gallery_images": gallery_images})
# def firstpage(request): 
    
#     data=Gallery.objects.all()
    
    
#     product_ids = [pro.pk for pro in data]
#     product_vectors = [json.loads(pro.vector_data) for pro in data]
#     product_vectors = np.array(product_vectors)  # Combine list of NumPy arrays to one array
#     product_vectors = torch.tensor(product_vectors)
#     if 'user' in request.session:
#         print(request.session['user'])
#         user = users.objects.get(username=request.session['user'])
#         user_vector = json.loads(user.vector_data)
#         recommend_products = recommend_product(user_vector, product_vectors, product_ids,top_n=4) 
#         print(recommend_products)
#         products = [i[0] for i  in recommend_products]
#         preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(products)])
#         products = product.objects.filter(pk__in=products).order_by(preserved_order)
#         print(products)
        
        
#     data2=Gallery.objects.all()[:8]
#     allp=filter(data2)
#     data3=Gallery.objects.all()[::-1][:3]
#     addp=filter(data3)
#     return render(request,'firstpage.html',{'data':data,'allp':allp,'addp':addp,'user':getuser(request),'type':types(request)})
    
#     # Get the latest 4 products by ordering them by ID in descending order
#     gallery_images = Gallery.objects.all().order_by('-id')[:4]  # This will give you the latest 4 products by ID
#     if request.user.is_authenticated:
#         cart_item_count = Cart.objects.filter(user=request.user).count()
#     else:
#         cart_item_count = 0 

#     return render(request, "firstpage.html", {
#         "gallery_images": gallery_images,
#         "cart_item_count": cart_item_count
#     })







def firstpage(request):
    # Fetch all Gallery objects
    data = Gallery.objects.all()
    
    # Prepare product vectors and IDs, skipping objects with None or empty vector_data
    product_ids = []
    product_vectors = []
    for pro in data:
        if pro.vector_data:  # Check if vector_data is not None or empty
            try:
                vector = json.loads(pro.vector_data)
                product_ids.append(pro.pk)
                product_vectors.append(vector)
            except json.JSONDecodeError:
                continue  # Skip invalid JSON

    # Convert product vectors to tensor
    product_vectors = torch.tensor(product_vectors) if product_vectors else torch.tensor([])

    # Initialize recommended products
    recommended_products = []

    # Generate recommendations for authenticated user
    if request.user.is_authenticated:
        try:
            user_obj = users.objects.get(user=request.user)  # Use user field
            if user_obj.vector_data:  # Check if user has vector_data
                user_vector = torch.tensor(json.loads(user_obj.vector_data))
                if product_vectors.numel() > 0:  # Ensure there are product vectors
                    recommended = recommend_product(user_vector, product_vectors, product_ids, top_n=4)
                    product_pks = [rec[0] for rec in recommended]
                    # Preserve order of recommended products
                    preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(product_pks)])
                    recommended_products = Gallery.objects.filter(pk__in=product_pks).order_by(preserved_order)
        except users.DoesNotExist:
            pass  # No users object, skip recommendations
        except json.JSONDecodeError:
            pass  # Invalid user vector_data, skip recommendations

    # Fallback: If no recommendations, select random products
    if not recommended_products:
        recommended_products = Gallery.objects.order_by('?')[:4]

    # Get latest products for display
    gallery_images = Gallery.objects.all().order_by('-id')[:4]  # Latest 4 products
    data2 = Gallery.objects.all()[:8]  # First 8 products
    data3 = Gallery.objects.all().order_by('-id')[:3]  # Latest 3 products

    # Cart item count
    cart_item_count = Cart.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    return render(request, 'firstpage.html', {
        'gallery_images': gallery_images,
        'products': recommended_products,  # Recommended products
        'allp': data2,  # First 8 products
        'addp': data3,  # Latest 3 products
        'user': getuser(request),
        'type': types(request),
        'cart_item_count': cart_item_count
    })




def allproducts(request): 
    gallery_images = Gallery.objects.all()  
    if request.user.is_authenticated:
        cart_item_count = Cart.objects.filter(user=request.user).count()
    else:
        cart_item_count = 0 
    return render(request, "allproduct.html", {
        "gallery_images": gallery_images,
        "cart_item_count": cart_item_count
    })   
model = SentenceTransformer('all-MiniLM-L6-v2')

def usersignup(request):
    if request.method == 'POST':  # Use request.method for clarity
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confpassword')

        # Validation checks
        if not all([username, email, password, confirmpassword]):
            messages.error(request, 'All fields are required.')
        elif confirmpassword != password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            try:
                # Create and save the Django User
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Create meaningful initial data for the user vector
                user_datas = [{
                    "user_id": user.id,
                    "product": "new_user",  # Placeholder; replace with meaningful data if possible
                    "search": "initial_signup"  # Placeholder; replace with meaningful data if possible
                }]
                df = pd.DataFrame(user_datas)

                # Generate the vector using the vectorize_user_with_search function
                user_vectors = vectorize_user_with_search(df)

                # Check if vectors were successfully created
                if user_vectors and len(user_vectors) > 0:
                    # Create a users model instance
                    user_profile = users.objects.create(
                        user=user,
                        vector_data=json.dumps(user_vectors[0].tolist())
                    )
                    user_profile.save()
                    print(f"Vector created and saved successfully for user: {username}")
                else:
                    print(f"Failed to create vector for user: {username}")

                messages.success(request, "Account created successfully!")
                return redirect('userlogin')

            except Exception as e:
                # Log the error but allow user creation
                print(f"Error creating vector for user {username}: {str(e)}")
                # Still create a users model instance without vector data
                user_profile = users.objects.create(user=user, vector_data=None)
                user_profile.save()
                messages.success(request, "Account created successfully, but personalization data could not be initialized.")
                return redirect('userlogin')

    return render(request, "userregister.html")
def userlogin(request):
    if 'username' in request.session:
        return redirect('firstpage')  
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if user.is_superuser:
                return redirect('adminpage')
            return redirect('firstpage')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'userlogin.html')
# def product(request,id):
#     gallery_images =Gallery.objects.filter(pk=id)
#     return render(request,'products.html',{"gallery_images": gallery_images,})
model = SentenceTransformer('all-MiniLM-L6-v2')

# @login_required(login_url='userlogin')
# def product(request, id):
#     try:
#         product = Gallery.objects.get(id=id)
#         gallery_images = Gallery.objects.filter(id=id)
#         cart_items = Cart.objects.filter(user=request.user)
#         cart_product_ids = [item.product.id for item in cart_items]
#     except Gallery.DoesNotExist:
#         messages.error(request, "Product not found.")
#         return redirect('product_not_found')

#     # Use the 'user' field instead of 'name' for get_or_create
#     user_name, created = users.objects.get_or_create(user=request.user)

#     # Track view history
#     ViewHistory.objects.create(user=user_name, product=product)

#     # Prepare view history data for vectorization
#     existing_user_data = ViewHistory.objects.filter(user=user_name)
#     existing_products = [history.product.name for history in existing_user_data]
#     data = [{
#         'user_id': user_name.id,
#         'product': ','.join(existing_products),
#         'search': ''
#     }]
#     df = pd.DataFrame(data)

#     # Vectorize and save
#     try:
#         user_vectors = vectorize_user_with_search(df)
#         user_name.vector_data = json.dumps(user_vectors[0].tolist())
#         user_name.save()
#     except Exception as e:
#         print(f"Vectorization failed: {e}")

#     # Fetch reviews
#     rs = reviews.objects.filter(pname=product)
    
#     # Check if user has reviewed
#     isReviewed = reviews.objects.filter(uname=user_name, pname=product).exists()

#     context = {
#         'gallery_images': gallery_images,
#         'cart_product_ids': cart_product_ids,
#         'isReviewed': isReviewed,
#         'reviews': rs,
#     }
#     return render(request, 'products.html', context)




@login_required(login_url='userlogin')
def product(request, id):
    try:
        product = Gallery.objects.get(id=id)
        gallery_images = Gallery.objects.filter(id=id)
        cart_items = Cart.objects.filter(user=request.user)
        cart_product_ids = [item.product.id for item in cart_items]
    except Gallery.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('firstpage')  # Update to your actual redirect

    if request.user.is_authenticated:
        # Get or create user profile
        user_name, created = users.objects.get_or_create(user=request.user)

        # Track view history
        ViewHistory.objects.create(user=user_name, product=product)

        # Prepare view history data for vectorization
        existing_user_data = ViewHistory.objects.filter(user=user_name)
        existing_products = [history.product.name for history in existing_user_data]
        data = [{
            'user_id': user_name.id,
            'product': ','.join(existing_products),
            'search': ''
        }]
        df = pd.DataFrame(data)

        # Vectorize and save
        try:
            user_vectors = vectorize_user_with_search(df)
            user_name.vector_data = json.dumps(user_vectors[0].tolist())
            user_name.save()
        except Exception as e:
            print(f"Vectorization failed: {e}")
    else:
        user_name = None

    # Fetch reviews
    rs = reviews.objects.filter(pname=product)

    # Check if user has reviewed
    isReviewed = reviews.objects.filter(uname__user=request.user, pname=product).exists() if request.user.is_authenticated else False

    context = {
        'gallery_images': gallery_images,
        'cart_product_ids': cart_product_ids,
        'isReviewed': isReviewed,
        'reviews': rs,
    }
    return render(request, 'products.html', context)



def review(request):
    return render(request,"review.html")
def aboutus(request):
    return render(request,"aboutus.html")
def adminpage(request):
    data = Gallery.objects.all()
    gallery_images = Gallery.objects.filter(user=request.user)
    return render(request,'adminpage.html',{"gallery_images": gallery_images})
def admin_users(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        # Redirect non-admin users or unauthenticated users
        return redirect('loginuser')

    users = User.objects.all()  # Fetch all users
    return render(request, 'admin_users.html', {'users': users})
def delete_g(request,id):
    feeds=Gallery.objects.filter(pk=id)
    feeds.delete()
    return redirect('adminpage')


def add(request):
    return render(request,"index.html")
def logoutuser(request):
    logout(request)
    request.session.flush()
    return redirect(firstpage)
@login_required
def edit_g(request, id):
    gallery_image = get_object_or_404(Gallery, pk=id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get("todo")
        discription = request.POST.get("description")
        price = request.POST.get("date")
        quanty = request.POST.get("quant")
        mod = request.POST.get("model") 
        off = request.POST.get("offers")

        # Check required fields
        if not all([name, price, quanty, mod, off]):
            messages.error(request, "All fields are required.")
            return render(request, 'index.html', {'data1': gallery_image})

        # Update text fields
        gallery_image.name = name
        gallery_image.discription = discription
        gallery_image.price = price
        gallery_image.quantity = quanty
        gallery_image.model = mod
        gallery_image.offers = off

        # Conditionally update images if provided
        if 'image' in request.FILES:
            gallery_image.feedimage = request.FILES['image']
        if 'image1' in request.FILES:
            gallery_image.image1 = request.FILES['image1']
        if 'image2' in request.FILES:
            gallery_image.image2 = request.FILES['image2']
        if 'image3' in request.FILES:
            gallery_image.image3 = request.FILES['image3']

        gallery_image.save()
        messages.success(request, "Gallery item updated successfully!")
        return redirect('adminpage')

    return render(request, 'index.html', {'data1': gallery_image})
# @login_required(login_url='userlogin')  # Redirect to your login page
# def add_to_cart(request, id):
#     product = get_object_or_404(Gallery, id=id)
#     cart_item, created = Cart.objects.get_or_create(
#         user=request.user,
#         product=product,
#         defaults={'quantity': 1}
#     )
#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()
#     return redirect('cart_view')
# @login_required(login_url='userlogin')
# def add_to_cart(request, id):
#     if 'username' in request.session:
#         try:
#             product = Gallery.objects.get(id=id)
#         except Gallery.DoesNotExist:
        
#             return redirect('product_not_found')  
    
#         cart_item, created = Cart.objects.get_or_create(
#             user=request.user,
#             product=product,
        
#         )
#         if not created:
#             if cart_item.product.quantity > cart_item.quantity:
#                 cart_item.quantity += 1
#             else:
#                 messages.error(request, "out of stock.")
#                 return redirect('cart_view')
#         else:
#             cart_item.quantity = 1
#             cart_item.save()
#             return redirect('cart_view')



@login_required(login_url='userlogin')  # Ensure user is logged in
def add_to_cart(request, id):
    if 'username' in request.session:  # Check if session contains 'username'
        try:
            product = Gallery.objects.get(id=id)
        except Gallery.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('product_not_found')

        # Check if product is already in the cart
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            if cart_item.product.quantity > cart_item.quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, "Out of stock.")
        else:
            cart_item.quantity = 1
            cart_item.save()

        return redirect('cart_view')  # Make sure a response is always returned

    else:
        messages.error(request, "You must be logged in to add items to the cart.")
        return redirect('userlogin')  # Redirect to login page if not logged in


# @login_required
# def increment_cart(request, id):
#     cart_item = get_object_or_404(Cart, pk=id, user=request.user)
#     cart_item.quantity += 1
#     cart_item.save()
#     return redirect('cart_view')

@login_required
def increment_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.product.quantity > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, "Not enough stock available.")

    return redirect('cart_view')

# @login_required
# def decrement_cart(request, id):
#     cart_item = get_object_or_404(Cart, pk=id, user=request.user)
#     if cart_item.quantity > 1:
#         cart_item.quantity -= 1
#         cart_item.save()
#     else:
#         cart_item.delete()
#     return redirect('cart_view')

@login_required
def decrement_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart_view')

# @login_required
# def cart_view(request):
#     cart_items = Cart.objects.filter(user=request.user)
#     total_price = sum(item.product.price * item.quantity for item in cart_items)
#     return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required(login_url='userlogin')
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    cart_item_count = cart_items.count()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'cart_item_count': cart_item_count})

@login_required
def delete_cart(request, id):
    cart_item = get_object_or_404(Cart, pk=id, user=request.user)
    cart_item.delete()
    return redirect('cart_view')

@login_required(login_url='userlogin')
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')

    # Calculate total price and subtotals
    total_price = 0
    cart_items_with_subtotal = []
    for item in cart_items:
        subtotal = item.product.price * item.quantity
        total_price += subtotal
        cart_items_with_subtotal.append({
            'item': item,
            'subtotal': subtotal
        })

    # Fetch the most recent address for the user
    current_address = Address.objects.filter(user=user).order_by('-id').first()

    if request.method == "POST":
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        # Validate address
        if not address:
            messages.error(request, "Please provide a delivery address.")
            return render(request, "checkout.html", {
                'cart_items_with_subtotal': cart_items_with_subtotal,
                'total_price': total_price,
                'current_address': current_address
            })

        # Validate payment method
        if payment_method not in ['COD', 'ONLINE']:
            messages.error(request, "Invalid payment method.")
            return render(request, "checkout.html", {
                'cart_items_with_subtotal': cart_items_with_subtotal,
                'total_price': total_price,
                'current_address': current_address
            })

        if payment_method == 'ONLINE':
            # Store cart data in session for Razorpay payment
            cart_data = {
                'cart_items': [
                    {
                        'product_id': item.product.id,
                        'quantity': item.quantity,
                        'price': float(item.product.price),
                        'subtotal': float(item.product.price * item.quantity)
                    } for item in cart_items
                ],
                'total_price': float(total_price),
                'address': address,
                'payment_method': payment_method,
                'name': user.username
            }
            request.session['cart_data'] = cart_data
            return redirect('order_payment1')  # Redirect to order_payment1 without id

        else:  # COD
            for item in cart_items:
                if item.quantity > item.product.quantity:
                    messages.error(request, f"Not enough stock available for {item.product.name}.")
                    return render(request, "checkout.html", {
                        'cart_items_with_subtotal': cart_items_with_subtotal,
                        'total_price': total_price,
                        'current_address': current_address
                    })

                order = Order.objects.create(
                    user=user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.product.price * item.quantity,
                    address=address,
                    payment_method=payment_method,
                    status="Pending"
                )

                # Reduce product stock
                item.product.quantity -= item.quantity
                item.product.save()

                # Send email to admin
                admin_email = "jiyajiya8812@gmail.com"
                subject = f"New Order Placed - {order.id}"
                message = f"""
                New Order Placed!

                Order ID: {order.id}
                User: {user.username}
                Product: {item.product.name}
                Quantity: {item.quantity}
                Total Price: ₹{order.total_price}
                Address: {address}
                Payment Method: {payment_method}

                Please process the order in the admin panel.
                """
                send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

            # Clear the cart
            cart_items.delete()

            messages.success(request, "Order placed successfully! An email has been sent to the admin.")
            return redirect('order_success')

    context = {
        'cart_items_with_subtotal': cart_items_with_subtotal,
        'total_price': total_price,
        'current_address': current_address
    }
    return render(request, 'checkout.html', context)
def sample(request):
    return redirect('add_to_cart')

# @login_required
# def buy_now(request, product_id):
#     if 'username' in request.session:
#         product = get_object_or_404(Gallery, id=product_id)

#         if request.method == "POST":
#             quantity = int(request.POST.get("quantity", 1))
#             address = request.POST.get("address")
#             payment_method = request.POST.get("payment_method")
#             total_price = product.price * quantity  

#             order = Order.objects.create(
#                 user=request.user,
#                 product=product,
#                 quantity=quantity,
#                 total_price=total_price,
#                 address=address,
#                 payment_method=payment_method,
#                 status="Pending"
#             )

#             # Send email to admin
#             admin_email = "jiyajiya8812@gmail.com"  # Replace with the admin's email
#             subject = f"New Order Placed - {order.id}"
#             message = f"""
#             New Order Placed!

#             Order ID: {order.id}
#             User: {request.user.username}
#             Product: {product.name}
#             Quantity: {quantity}
#             Total Price: ₹{total_price}
#             Address: {address}
#             Payment Method: {payment_method}

#             Please process the order in the admin panel.
#             """

#             send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

#             messages.success(request, "Order placed successfully! An email has been sent to the admin.")

#             return redirect('order_confirmation', order_id=order.id)

#         return render(request, "buy_now.html", {"product": product})

#     else:
#         return redirect('userlogin')
def buy_now(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to place an order.")
        return redirect('login')

    product = get_object_or_404(Gallery, id=product_id)
    current_address = Address.objects.filter(user=request.user).order_by('-id').first()

    if request.method == "POST":
        name = request.POST.get("name")
        quantity = request.POST.get("quantity")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        if not all([name, quantity, address, payment_method]):
            messages.error(request, "All fields are required.")
            return render(request, "buy_now.html", {"product": product, "current_address": current_address})

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid quantity.")
            return render(request, "buy_now.html", {"product": product, "current_address": current_address})

        if quantity > product.quantity:
            messages.error(request, "Not enough stock available.")
            return render(request, "buy_now.html", {"product": product, "current_address": current_address})

        total_price = product.price * quantity

        if payment_method == "ONLINE":
            request.session['order_data'] = {
                'product_id': product_id,
                'quantity': quantity,
                'total_price': str(total_price),
                'address': address,
                'payment_method': payment_method,
                'name': name
            }
            return redirect('order_payment', id=product_id)
        else:  # COD
            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                total_price=Decimal(total_price),
                address=address,
                payment_method=payment_method,
                status=PaymentStatus.PENDING  # Remove .value
            )

            product.quantity -= quantity
            product.save()

            admin_email = "jiyajiya8812@gmail.com"
            subject = f"New Order Placed - {order.id}"
            message = f"""
            New Order Placed!
            Order ID: {order.id}
            User: {request.user.username}
            Product: {product.name}
            Quantity: {quantity}
            Total Price: ₹{total_price}
            Address: {address}
            Payment Method: {payment_method}
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

            messages.success(request, "Order placed successfully!")
            return redirect('order_confirmation', order_id=order.id)

    return render(request, "buy_now.html", {"product": product, "current_address": current_address})
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})














def getuser(request):
    return request.session.get('user')


# def filter_price(data, price):
#     price2 = []
#     for i in data:
#         for j in price:
#             if i.pk == j.product.pk:
#                 price2.append(j)
#                 break
#     return price2


def types(request):
    type2 = []
    for i in Gallery.objects.all():
        if i.model and i.model not in type2:
            type2.append(i.model)
    return type2

# def search_func(request):
#     if request.method == 'POST':
#         inp = request.POST['search']
        

#         auth_user = None
#         users_data = None

#         if 'user' in request.session:
#             try:
#                 auth_user = User.objects.get(username=request.session['user'])
#                 users_data = users.objects.get(name=auth_user)
#             except (User.DoesNotExist, users.DoesNotExist):
#                 auth_user = None
#                 users_data = None

#             if users_data and auth_user:
#                 # Save search query
#                 SearchHistory.objects.create(query=inp, user=users_data)

#                 # Get user search history
#                 user_search = SearchHistory.objects.filter(user=users_data)
#                 user_search = [s.query for s in user_search]

#                 # Get view history
#                 user_products = ViewHistory.objects.filter(user=users_data)
#                 user_products = [s.product.name for s in user_products]

#                 # Prepare data for vectorization
#                 user_data = [{
#                     'user_id': auth_user.id,
#                     'product': ','.join(user_products) if user_products else '',
#                     'search': ','.join(user_search) if user_search else ''
#                 }]

#                 df = pd.DataFrame(user_data)

#                 # Vectorize
#                 user_vectors = vectorize_user_with_search(df)
#                 users_data.vector_data = json.dumps(user_vectors[0].tolist())
#                 users_data.save()

#         # Search for products by name or category
#         products_by_name = Gallery.objects.filter(name__icontains=inp)  # Changed from iexact to icontains
#         products_by_category = Gallery.objects.filter(model__name__icontains=inp)  # Changed from iexact to icontains
#         pro_name = (products_by_name | products_by_category).distinct()

        

#         return render(request, 'search_results.html', {
#             'shoe_category': types(request),
#             'user': getuser(request),
#             'query': inp,
#             'products': pro_name
#         })
    
#     # Handle GET requests - redirect to home or show empty search
#     return redirect('firstpage') 








####################################my code###############################################







@login_required(login_url='userlogin')
def search_func(request):
    if request.method == 'POST':
        inp = request.POST.get('search', '').strip()
        
        if not inp:
            return render(request, 'search_results.html', {
                'shoe_category': types(request),
                'user': getuser(request),
                'query': '',
                'products': [],
                'error': 'Search query cannot be empty'
            })

        auth_user = request.user
        users_data, created = users.objects.get_or_create(user=auth_user)

        # Save search query
        SearchHistory.objects.create(query=inp, user=users_data)

        # Get user search history
        user_search = SearchHistory.objects.filter(user=users_data)
        user_search = [s.query for s in user_search]

        # Get view history
        user_products = ViewHistory.objects.filter(user=users_data)
        user_products = [s.product.name for s in user_products]

        # Prepare data for vectorization
        user_data = [{
            'user_id': auth_user.id,
            'product': ','.join(user_products) if user_products else '',
            'search': ','.join(user_search) if user_search else ''
        }]

        df = pd.DataFrame(user_data)

        # Vectorize
        try:
            user_vectors = vectorize_user_with_search(df)
            users_data.vector_data = json.dumps(user_vectors[0].tolist())
            users_data.save()
        except Exception as e:
            print(f"Vectorization failed: {e}")

        # Search for products by name or model
        products_by_name = Gallery.objects.filter(name__icontains=inp)
        products_by_category = Gallery.objects.filter(model__icontains=inp)
        pro_name = (products_by_name | products_by_category).distinct()

        return render(request, 'search_results.html', {
            'shoe_category': types(request),
            'user': getuser(request),
            'query': inp,
            'products': pro_name
        })
    
    # Handle GET requests - redirect to home
    return redirect('firstpage')







def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        order.status = new_status
        order.save()
        return redirect("adminpage")  # Redirect back to admin page

    return render(request, "update_order.html", {"order": order})
# def usres_g(request):
#     return render(request,'users.html')
def admin_orders(request):
    #    orders = Order.objects.select_related('user', 'product').all() 
    orders = Order.objects.select_related('user', 'product').order_by('-id') # Fetch orders with related user & product

    return render(request, 'admin_orders.html', {"orders": orders})
# def admin_orders(request):
#     orders = Order.objects.select_related('user', 'product')  # Fetch orders with related user & product
#     return render(request, 'admin_orders.html', {'orders': orders})



# def update_order_status(request, order_id):
#     if request.method == 'POST':
#         order = get_object_or_404(Order, id=order_id)
#         new_status = request.POST.get('status')
#         order.status = new_status
#         order.save()
#     return redirect('admin_orders')






def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Only proceed if the status is actually changing
        if order.status != new_status:
            order.status = new_status
            order.save()

            # Define status-specific email content
            status_messages = {
                'pending': 'Your order is currently pending.',
                'success': 'Your order has been successfully processed.',
                'shipped': 'Great news! Your order has been shipped.',
                'delivered': 'Your order has been delivered. Thank you for shopping with us!'
            }

            # Prepare email details
            subject = f'Order Status Update - Order #{order.id}'
            message = (
                f'Dear {order.user.username},\n\n'
                f'The status of your order #{order.id} has been updated.\n'
                f'New Status: {new_status.capitalize()}\n'
                f'{status_messages.get(new_status, "Your order status has been updated.")}\n\n'
                f'Product: {order.product.name} ({order.product.model})\n'
                f'Quantity: {order.quantity}\n'
                f'Total Price: {order.total_price}\n\n'
                f'Thank you,\nShoes Cart'
            )
            recipient_email = order.user.email

            # Send email
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error if email sending fails (optional)
                print(f"Failed to send email to {recipient_email}: {e}")

    return redirect('admin_orders')




# @login_required(login_url='userlogin')
# def my_profile(request):
#     user = request.user

#     # Handle form submission for updating user details
#     if request.method == 'POST':
#         # Get the data from the form submission
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         address = request.POST.get('address')

#         # Update the user's profile fields
#         user.username = username if username else user.username
#         user.email = email if email else user.email
#         if hasattr(user, 'userprofile'):
#             user.userprofile.address = address if address else user.userprofile.address
#             user.userprofile.save()

#         # Save the updated user details
#         user.save()

#         # Show a success message
#         messages.success(request, "Profile updated successfully.")
#         return redirect('my_profile')  # Redirect back to the profile page

#     # If the request method is GET, show the current user details
#     return render(request, 'my_profile.html', {'user': user})




@login_required(login_url='userlogin')
def profile_view(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'addresses': addresses,
        'email': request.user.email,
        'username': request.user.username,
        'orders': orders,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='userlogin')
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not address:
            errors['address'] = 'Address is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        elif not phone.isdigit() or len(phone) != 10:
            errors['phone'] = 'Phone number must be 10 digits.'
        
        if not errors:
            Address.objects.create(
                user=request.user,
                name=name,
                address=address,
                phone=phone
            )
            messages.success(request, 'Address added successfully!')
            return redirect('profile')
        else:
            return render(request, 'address_form.html', {
                'errors': errors,
                'name': name,
                'address': address,
                'phone': phone,
                'action': 'Add'
            })
    
    return render(request, 'address_form.html', {'action': 'Add'})
@login_required(login_url='userlogin')
def edit_address(request, address_id):
    address_obj = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')
        
        errors = {}
        if not name:
            errors['name'] = 'Name is required.'
        if not address:
            errors['address'] = 'Address is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        elif not phone.isdigit() or len(phone) != 10:
            errors['phone'] = 'Phone number must be 10 digits.'
        
        if not errors:
            address_obj.name = name
            address_obj.address = address
            address_obj.phone = phone
            address_obj.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('profile')
        else:
            return render(request, 'address_form.html', {
                'errors': errors,
                'name': name,
                'address': address,
                'phone': phone,
                'action': 'Edit'
            })
    
    return render(request, 'address_form.html', {
        'name': address_obj.name,
        'address': address_obj.address,
        'phone': address_obj.phone,
        'action': 'Edit'
    })
@login_required(login_url='userlogin')
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('profile')
    
    return render(request, 'confirm_delete.html', {'address': address})
@login_required(login_url='userlogin')
def edit_email(request):
    user = request.user
    
    if request.method == 'POST':
        email = request.POST.get('email', '')
        
        errors = {}
        if not email:
            errors['email'] = 'Email is required.'
        elif '@' not in email:
            errors['email'] = 'Please enter a valid email address.'
        elif User.objects.filter(email=email).exclude(id=user.id).exists():
            errors['email'] = 'This email is already in use.'
            
        if not errors:
            user.email = email
            user.save()
            messages.success(request, 'Email updated successfully!')
            return redirect('profile')
        else:
            return render(request, 'email_form.html', {
                'errors': errors,
                'email': email
            })
    
    return render(request, 'email_form.html', {
        'email': user.email
    })

@login_required(login_url='userlogin')
def edit_username(request):
    user = request.user
    
    if request.method == 'POST':
        username = request.POST.get('username', '')
        
        errors = {}
        if not username:
            errors['username'] = 'Username is required.'
        elif len(username) < 4:
            errors['username'] = 'Username should be at least 4 characters long.'
        elif User.objects.filter(username=username).exclude(id=user.id).exists():
            errors['username'] = 'This username is already taken.'
            
        if not errors:
            user.username = username
            user.save()
            # Update session to reflect new username
            request.session['username'] = username
            messages.success(request, 'Username updated successfully!')
            return redirect('profile')
        else:
            return render(request, 'username_form.html', {
                'errors': errors,
                'username': username
            })
    
    return render(request, 'username_form.html', {
        'username': user.username
    })
    
    
    
@login_required(login_url='userlogin')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Keep user logged in after password change
            login(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            return render(request, 'password_form.html', {
                'errors': form.errors,
                'old_password': request.POST.get('old_password', ''),
                'new_password1': request.POST.get('new_password1', ''),
                'new_password2': request.POST.get('new_password2', '')
            })
    
    return render(request, 'password_form.html', {})    


# def logout_view(request):
#     logout(request)
#     return redirect('firstpage')



#####################payment#######################


def order_payment(request, id):
    try:
        print("Debug: Entering order_payment view")
        order_data = request.session.get('order_data')
        print(f"Debug: order_data = {order_data}")
        if not order_data or str(order_data.get('product_id')) != str(id):
            print("Debug: Invalid payment request - session data mismatch")
            return render(request, "error.html", {"message": "Invalid payment request", "product_id": id})

        product = get_object_or_404(Gallery, pk=id)
        user = request.user
        total_price = Decimal(order_data['total_price'])
        print(f"Debug: total_price = {total_price}")
        quantity = order_data['quantity']
        address = order_data['address']
        payment_method = order_data['payment_method']
        name = order_data['name']

        if total_price != product.price * quantity:
            print("Debug: Invalid total price")
            raise ValueError("Invalid total price")

        amount_in_paise = int(total_price * 100)
        if amount_in_paise <= 0:
            print("Debug: Amount must be greater than zero")
            raise ValueError("Amount must be greater than zero")

        print(f"Debug: Initializing Razorpay client with key_id={settings.RAZORPAY_KEY_ID}")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print("Debug: Creating Razorpay order")
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })
        print(f"Debug: Razorpay order created: {razorpay_order}")

        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            total_price=total_price,
            address=address,
            payment_method=payment_method,
            provider_order_id=razorpay_order['id'],
            status=PaymentStatus.PENDING
        )

        print("Debug: Clearing session data")
        del request.session['order_data']
        callback_url = f"{request.scheme}://{request.get_host()}/razorpay/callback/"

        print("Debug: Rendering payment.html")
        return render(
            request,
            "payment.html",
            {
                "callback_url": callback_url,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": order,
                "amount": amount_in_paise,
                "product": product,
                "name": name
            }
        )
    except Exception as e:
        print(f"Error in order_payment: {str(e)}")
        return render(request, "error.html", {
            "message": f"Payment initiation failed: {str(e)}",
            "product_id": id
        })
# @csrf_exempt
# def callback(request):
#     def verify_signature(response_data):
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         try:
#             client.utility.verify_payment_signature(response_data)
#             return True
#         except Exception as e:
#             print(f"Signature verification failed: {e}")
#             return False

#     if request.method != 'POST':
#         return render(request, 'callback.html', {'status': 'Invalid request'})

#     print(f"Callback POST data: {request.POST}")  # Debug log

#     if "razorpay_signature" in request.POST:
#         payment_id = request.POST.get('razorpay_payment_id', '')
#         provider_order_id = request.POST.get('razorpay_order_id', '')
#         signature_id = request.POST.get('razorpay_signature', '')

#         try:
#             order = Order.objects.get(provider_order_id=provider_order_id)
#         except Order.DoesNotExist:
#             print(f"Order not found for provider_order_id: {provider_order_id}")
#             return render(request, 'callback.html', {'status': 'Order not found'})

#         # Verify payment signature
#         if verify_signature({
#             'razorpay_payment_id': payment_id,
#             'razorpay_order_id': provider_order_id,
#             'razorpay_signature': signature_id
#         }):
#             order.payment_id = payment_id
#             order.signature_id = signature_id
#             order.status = 'Completed'
#             order.save()

#             # Reduce product stock
#             order.product.quantity -= order.quantity
#             order.product.save()

#             # Clear the cart
#             Cart.objects.filter(user=order.user).delete()

#             return render(request, 'callback.html', {'status': 'Completed'})
#         else:
#             order.status = 'Cancelled'
#             order.save()
#             print(f"Signature verification failed for order: {order.id}")
#             return render(request, 'callback.html', {'status': 'Cancelled'})
#     else:
#         # Handle payment failure
#         try:
#             error_metadata = json.loads(request.POST.get('error[metadata]', '{}'))
#             provider_order_id = error_metadata.get('order_id', '')
#             payment_id = error_metadata.get('payment_id', '')

#             try:
#                 order = Order.objects.get(provider_order_id=provider_order_id)
#                 order.payment_id = payment_id
#                 order.status = 'Cancelled'
#                 order.save()
#                 print(f"Payment failed for order: {order.id}")
#                 return render(request, 'callback.html', {'status': 'Cancelled'})
#             except Order.DoesNotExist:
#                 print(f"Order not found for provider_order_id: {provider_order_id}")
#                 return render(request, 'callback.html', {'status': 'Order not found'})
#         except json.JSONDecodeError:
#             print("Invalid error metadata received")
#             return render(request, 'callback.html', {'status': 'Invalid error metadata'})


# def order_payment(request):
#     if request.method == "POST":
#         name = request.POST.get("name")
#         amount = request.POST.get("amount")
#         client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#         razorpay_order = client.order.create(
#             {"amount": int(amount) * 100, "currency": "INR", "payment_capture": "1"}
#         )
#         order_id=razorpay_order['id']
#         order = Order.objects.create(
#             name=name, amount=amount, provider_order_id=order_id
#         )
#         order.save()
#         return render(
#             request,
#             "index.html",
#             {
#                 "callback_url": "http://" + "127.0.0.1:8000" + "razorpay/callback",
#                 "razorpay_key": settings.RAZORPAY_KEY_ID,
#                 "order": order,
#             },
#         )
#     return render(request, "index.html")



@csrf_exempt
def callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        if not all([payment_id, provider_order_id, signature_id]):
            print("Error in callback: Missing Razorpay parameters.")
            return render(request, "callback.html", context={"status": "failure", "message": "Missing payment parameters"})

        try:
            order = Order.objects.get(provider_order_id=provider_order_id)
        except Order.DoesNotExist:
            print("Error in callback: Order not found.")
            return render(request, "callback.html", context={"status": "failure", "message": "Order not found"})

        order.payment_id = payment_id
        order.signature_id = signature_id

        response_data = {
            "razorpay_order_id": provider_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature_id,
        }

        if verify_signature(response_data):
            order.status = PaymentStatus.SUCCESS
            order.product.quantity -= order.quantity
            order.product.save()
        else:
            order.status = PaymentStatus.FAILED
            print("Signature verification failed")

        order.save()

        if order.status == PaymentStatus.SUCCESS:
            admin_email = "jiyajiya8812@gmail.com"
            subject = f"New Order Confirmed - {order.id}"
            message = f"""
            Order Confirmed!
            Order ID: {order.id}
            User: {order.user.username}
            Product: {order.product.name}
            Quantity: {order.quantity}
            Total Price: ₹{order.total_price}
            Address: {order.address}
            Payment Method: {order.payment_method}
            """
            send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])

        return render(request, "callback.html", context={"status": order.status, "order_id": order.id})
    else:
        error_message = request.GET.get("error", "Invalid request")
        return render(request, "callback.html", context={"status": "failure", "message": error_message})
def order_success(request):
    return render(request, "order_success.html")





def order_payment1(request):
    try:
        print("Debug: Entering order_payment1 view")
        cart_data = request.session.get('cart_data')
        print(f"Debug: cart_data = {cart_data}")
        if not cart_data:
            print("Debug: No cart data in session")
            return render(request, "error.html", {"message": "Invalid payment request"})

        total_price = Decimal(cart_data['total_price'])
        address = cart_data['address']
        payment_method = cart_data['payment_method']
        name = cart_data['name']
        cart_items = cart_data['cart_items']
        user = request.user

        # Validate total price
        calculated_total = sum(Decimal(item['subtotal']) for item in cart_items)
        if total_price != calculated_total:
            print("Debug: Invalid total price")
            raise ValueError("Invalid total price")

        amount_in_paise = int(total_price * 100)
        if amount_in_paise <= 0:
            print("Debug: Amount must be greater than zero")
            raise ValueError("Amount must be greater than zero")

        print(f"Debug: Initializing Razorpay client with key_id={settings.RAZORPAY_KEY_ID}")
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print("Debug: Creating Razorpay order")
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })
        print(f"Debug: Razorpay order created: {razorpay_order}")

        # Create orders for each cart item
        order_ids = []
        for item_data in cart_items:
            product = get_object_or_404(Gallery, pk=item_data['product_id'])
            order = Order.objects.create(
                user=user,
                product=product,
                quantity=item_data['quantity'],
                total_price=Decimal(item_data['subtotal']),
                address=address,
                payment_method=payment_method,
                provider_order_id=razorpay_order['id'],
                status=PaymentStatus.PENDING
            )
            order_ids.append(str(order.id))

        print("Debug: Clearing session data")
        del request.session['cart_data']
        callback_url = f"{request.scheme}://{request.get_host()}/razorpay/callback1/"

        # Prepare description for Razorpay
        description = "Purchase of " + ", ".join([f"{item['quantity']} x {Gallery.objects.get(pk=item['product_id']).name}" for item in cart_items])

        print("Debug: Rendering payment1.html")
        return render(
            request,
            "payment1.html",
            {
                "callback_url": callback_url,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "order": {"id": razorpay_order['id'], "provider_order_id": razorpay_order['id']},
                "amount": amount_in_paise,
                "description": description,
                "name": name
            }
        )
    except Exception as e:
        print(f"Error in order_payment1: {str(e)}")
        return render(request, "error.html", {
            "message": f"Payment initiation failed: {str(e)}"
        })



@csrf_exempt
def callback_cart1(request):
    print("Debug: Entering callback1 view")  # Add this to confirm the view is called
    def verify_signature(response_data):
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id", "")
        provider_order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")

        print(f"Debug: payment_id={payment_id}, provider_order_id={provider_order_id}, signature_id={signature_id}")

        if not all([payment_id, provider_order_id, signature_id]):
            print("Error in callback: Missing Razorpay parameters.")
            return render(request, "callback.html", context={"status": "failure", "message": "Missing payment parameters"})

        # Use filter() to retrieve all orders
        orders = Order.objects.filter(provider_order_id=provider_order_id)
        print(f"Debug: Found {orders.count()} orders for provider_order_id={provider_order_id}")
        if not orders.exists():
            print("Error in callback: Orders not found.")
            return render(request, "callback.html", context={"status": "failure", "message": "Orders not found"})

        response_data = {
            "razorpay_order_id": provider_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature_id,
        }

        if verify_signature(response_data):
            for order in orders:
                print(f"Debug: Updating order ID={order.id}, Product={order.product.name}")
                order.payment_id = payment_id
                order.signature_id = signature_id
                order.status = PaymentStatus.SUCCESS
                order.product.quantity -= order.quantity
                order.product.save()
                order.save()

                # Send email to admin
                admin_email = "jiyajiya8812@gmail.com"
                subject = f"New Order Confirmed - {order.id}"
                message = f"""
                Order Confirmed!
                Order ID: {order.id}
                User: {order.user.username}
                Product: {order.product.name}
                Quantity: {order.quantity}
                Total Price: ₹{order.total_price}
                Address: {order.address}
                Payment Method: {order.payment_method}
                """
                send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email])
        else:
            for order in orders:
                order.status = PaymentStatus.FAILED
                order.save()
            print("Signature verification failed")

        # Clear the cart after successful payment
        if all(order.status == PaymentStatus.SUCCESS for order in orders):
            Cart.objects.filter(user=orders[0].user).delete()
            print("Debug: Cart cleared")

        return render(request, "callback.html", context={"status": orders[0].status, "order_id": provider_order_id})
    else:
        error_message = request.GET.get("error", "Invalid request")
        print(f"Debug: Non-POST request with error={error_message}")
        return render(request, "callback.html", context={"status": "failure", "message": error_message})












@login_required
def addReview(request, pk):
    try:
        prod = Gallery.objects.get(pk=pk)
    except Gallery.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('firstpage')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        description = request.POST.get('description')

        # Validate inputs
        if not rating or not description:
            messages.error(request, "Rating and description are required.")
            return redirect(reverse('product', args=[pk]))

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Invalid rating. Please select a rating between 1 and 5.")
            return redirect(reverse('product', args=[pk]))

        try:
            user_profile = users.objects.get(user=request.user)
        except users.DoesNotExist:
            messages.error(request, "User profile not found. Please contact support.")
            return redirect('userlogin')

        # Check for existing review
        if reviews.objects.filter(uname=user_profile, pname=prod).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect(reverse('product', args=[pk]))

        # Create and save review
        data = reviews.objects.create(
            rating=rating,
            description=description,
            uname=user_profile,
            pname=prod
        )
        data.save()

        # Update product rating
        rev = reviews.objects.filter(pname=prod)
        total = [i.rating for i in rev]
        if total:
            total_rating = round(sum(total) / len(total), 1)
            prod.rating = total_rating
        else:
            prod.rating = rating
        prod.save()

        # Vectorize product with reviews
        comments = [i.description for i in rev]
        pro_data = [{
            "pro_id": prod.id,
            "name": prod.name,
            "rating": prod.rating,
            "model": getattr(prod, 'model', ''),
            "reviews": ','.join(comments)
        }]
        df = pd.DataFrame(pro_data)
        try:
            product_vector = vectorize_product_with_reviews(df)
            prod.vector_data = json.dumps(product_vector[0].tolist())
            prod.save()
        except Exception as e:
            print(f"Vectorization failed: {e}")
            messages.warning(request, "Review saved, but vectorization failed. Contact support.")

        messages.success(request, "Review submitted successfully!")
        return redirect(reverse('product', args=[pk]))
    else:
        reviews_list = reviews.objects.filter(pname=prod)
        cart_items = Cart.objects.filter(user=request.user)
        cart_product_ids = [item.product.id for item in cart_items]
        isReviewed = reviews.objects.filter(uname__user=request.user, pname=prod).exists()
        context = {
            'gallery_images': [prod],
            'reviews': reviews_list,
            'cart_product_ids': cart_product_ids,
            'isReviewed': isReviewed
        }
        return render(request, 'products.html', context)
    
    
    
    
    
    
    
    
    
