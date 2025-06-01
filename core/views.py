from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
import stripe, stripe.error,json
from core.forms import *
from django.db.models import Count,Q
from django.contrib import messages
from core.models import *
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
from django.contrib.auth import login, authenticate
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import AnonymousUser , User
from django.contrib.auth import update_session_auth_hash


def custom_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authenticate user and log them in
            user = form.get_user()
            login(request, user)
            return redirect('custom_admin_dashboard')  # Redirect to custom admin dashboard if successful
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})



   
@never_cache
@login_required(login_url='/custom_login/')
def custom_admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')  # Redirect to login page if the user is not a superuser

    # Fetch your data to render (orders, products, etc.)
    orders = Order.objects.all()  # Replace with your actual model
    products = Product.objects.all()
    categories = Category.objects.all()
    banners = Banner.objects.all()

    # Generate category data with product count
    category_data = [
        {
            'category': category,
            'product_count': category.products.count()  # Get the count of related products
        }
        for category in categories
    ]

    return render(request, 'core/custom_dashboard.html', {
        'orders': orders,
        'products': products,
        'categories': categories,
        'category_data': category_data,  # Pass category_data to the template
        'banners': banners,
    })


def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        order_status = request.POST.get('order_status')
        order_delivered = request.POST.get('order_delivered') == 'on'
        order_received = request.POST.get('order_received') == 'on'

        # Update the order status and other fields based on the admin input
        if order_status:
            order.order_status = order_status  # Update the order status
        if order_delivered != order.order_delivered:
            order.order_delivered = order_delivered  # Update delivery status
        if order_received != order.order_received:
            order.order_received = order_received  # Update receipt status

        order.save()  # Save the updated order

        return redirect('custom_admin_dashboard')  # Redirect back to the dashboard after save

    return render(request, 'core/edit_order.html', {'order': order})




# Delete Order View
@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect('custom_admin_dashboard') 


def index(request):
    categories = Category.objects.all()  # Get all categories
    products = Product.objects.all()
    banner = Banner.objects.first()

    import logging
    # Search query handling
    search_query = request.GET.get('search', '').strip().lower()
    logger = logging.getLogger(__name__)
    logger.info(f"Search query: '{search_query}'")

    if search_query:
     products = products.filter(
        Q(name__icontains=search_query) |
        Q(desc__icontains=search_query) |
        Q(category__category_name__icontains=search_query)
    )
    logger.info(f"After search filter: {products}")
    # Filter by category
    category_id = request.GET.get('category', None)
    if category_id:
        products = products.filter(category_id=category_id)

    # Filter by price range
    min_price = request.GET.get('min_price', None)
    max_price = request.GET.get('max_price', None)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, 'core/index.html', {
        'products': products,
        'banner': banner,
        'search_query': search_query,
        'categories': categories,
    })



def orderlist(request):
    if Order.objects.filter(user=request.user,ordered=False).exists():
        order = Order.objects.get(user = request.user,ordered=False)
        return render(request,'core/orderlist.html',{'order':order})
    return render(request,'core/orderlist.html',{'message':"Your Cart is Empty"})

def product_list(request):
    # Get all products from the database
    products = Product.objects.all()
    return render(request, 'core/product_list.html', {'products': products})





def product_desc(request, pk):
    # Fetch the product by its primary key
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()

    # Calculate average rating
    if reviews.exists():
        avg_rating = sum([review.rating for review in reviews]) / reviews.count()
    else:
        avg_rating = None  # No reviews yet

    # Check if the user is authenticated before checking the wishlist
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    else:
        is_in_wishlist = False  # If user is not authenticated, consider product not in wishlist

    if request.method == 'POST':
        quantity = request.POST.get('quantity', 1)  # Get the quantity selected from the form

    # Render the product detail page with the product, reviews, average rating, and wishlist status
    return render(request, 'core/product_desc.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'is_in_wishlist': is_in_wishlist,  # Pass this variable to the template
    })





@login_required
def submit_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Handle form submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Ensure the user is submitting only one review per product
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.info(request, "You've already submitted a review for this product.")
                return redirect('product_reviews', pk=pk)  # Redirect to the reviews page if review exists

            # Save the new review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # Assign logged-in user
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('product_desc', pk=pk)  # Redirect back to the product page

    else:
        form = ReviewForm()

    return render(request, 'core/product_desc.html', {'form': form, 'product': product})


def product_reviews(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    return render(request, 'core/product_reviews.html', {'product': product, 'reviews': reviews})

@login_required
def add_to_cart(request, pk):
    # Check if the user is logged in, if not, redirect to login
    if not request.user.is_authenticated:
        return redirect('login')  # Replace 'login' with the name of your login URL

    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity', 1))  # Get quantity from the form, default to 1

    # Create or update the order item
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False,
    )

    # Get the active order for the user (if any)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if the product is already in the cart
        if order.items.filter(product__id=pk).exists():
            order_item.quantity += quantity  # Add the selected quantity to existing quantity
            order_item.save()
            messages.info(request, f"{quantity} more {product.name} added to cart.")
        else:
            order.items.add(order_item)
            order_item.quantity = quantity  # Set the correct quantity
            order_item.save()
            messages.info(request, f'{product.name} Added to cart!')
    else:
        # If no active order exists, create a new one
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        order_item.quantity = quantity  # Set the quantity
        order_item.save()
        messages.info(request, "Item Added to Cart")
        
    return redirect('product_desc', pk=pk)
    
def add_item(request,pk):
    product = Product.objects.get(pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False,
    )
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk= pk).exists():
            if order_item.quantity < product.product_available_count :
                order_item.quantity += 1
                order_item.save()
                messages.info(request,"Added Quantity Item")
                return redirect('orderlist')
            else:
                messages.info(request,'Soryy! Product is out of Stock')
                return redirect('orderlist')
        else:
            order.items.add(order_item)
            messages.info(request,"Item Added to Cart")
            return redirect('product_desc',pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"Item Added to Cart")
        return redirect('product_desc',pk=pk)
    
def remove_item(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__pk=pk).exists():
            order_item =OrderItem.objects.filter(
                product = item,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1 
                order_item.save()
            else:
                order_item.delete()
            messages.info(request,"Item Quantity was Updated")
            return redirect('orderlist')
        else:
            messages.info(request,"This Item is not in your Cart")
            return redirect('orderlist')
    else:
        messages.info(request,"You do not have Any order")
        return redirect('orderlist')
    

@login_required
def add_to_wishlist(request, pk):
    # Check if the user is logged in, if not, redirect to login page
    if not request.user.is_authenticated:
        return redirect('login')  # Make sure 'login' matches the URL name for your login page
    
    product = get_object_or_404(Product, pk=pk)

    # Check if the product is already in the wishlist
    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.info(request, "This product is already in your wishlist.")
    else:
        # Add product to wishlist if not already present
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.name} has been added to your wishlist.")
    
    return redirect('product_desc', pk=pk) 

# Remove product from the wishlist
def remove_from_wishlist(request, pk):
    product = Product.objects.get(pk=pk)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f"{product.name} has been removed from your wishlist.")
    else:
        messages.info(request, "This product is not in your wishlist.")
    return redirect('wishlist')

# View the user's wishlist
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'core/wishlist.html', {'wishlist_items': wishlist_items})
    
def checkout_page(request):
    # Get all existing addresses for the user
    existing_addresses = CheckoutAddress.objects.filter(user=request.user)

    if existing_addresses.exists():
        # If there are existing addresses, render the page with options to choose one
        return render(request, 'core/checkout_address_options.html', {
            'addresses': existing_addresses
        })
    else:
        # If no existing address, redirect to the address entry form
        return redirect('checkout_address')
    


def checkout_address(request):
    # Handle the case where user enters a new address
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            zip_code = form.cleaned_data.get('zip')

            checkout_address = CheckoutAddress(
                user=request.user,
                street_address=street_address,
                apartment_address=apartment_address,
                country=country,
                zip_code=zip_code,
            )
            checkout_address.save()
            return redirect('checkout_page')
    else:
        form = CheckoutForm()

    return render(request, 'core/checkout_address.html', {'form': form})

def select_existing_address(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        if address_id:
            selected_address = CheckoutAddress.objects.get(id=address_id, user=request.user)
            
            # Assuming the order object exists and is currently being processed
            order = Order.objects.get(user=request.user, ordered=False)  # Get the active order
            order.checkout_address = selected_address  # Save the selected address
            order.save()

            # Redirect to the next step, for example, the payment page or summary page
            return redirect('payment_option')  # Replace with your actual next step URL
    return redirect('checkout_page')


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def create_checkout_session(request):
    order = Order.objects.get(user=request.user, ordered=False)  # Get the order details
    total_amount = 0  
    line_items = []
    
    for item in order.items.all():
        discount_price = item.product.get_discount_price()
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(discount_price * 100),  # Price in cents (discounted price)
            },
            'quantity': item.quantity,
        })
        total_amount += int(discount_price * item.quantity * 100)

    # Create a checkout session with Stripe
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(f'/payment-success/?order_id={order.order_id}'),
        cancel_url=request.build_absolute_uri('/payment-cancelled/'),
    )

    return redirect(checkout_session.url, code=303)


def payment_option(request):
    # Check if the user has a valid order
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('checkout_page')

    return render(request, 'core/payment_option.html', {'order': order})


def payment_redirect(request, payment_method):
    try:
        # Try to get the user's current un-ordered (open) order
        order = Order.objects.get(user=request.user, ordered=False)
        print(f"Order found: {order}")
    except Order.DoesNotExist:
        print("No active order found.")
        # If no order exists or it has already been ordered, show an error message
        messages.error(request, "You don't have an active order.")
        return redirect('checkout_page')  # Redirect to checkout page or another appropriate page
    
    # Process payment methods
    if payment_method == 'stripe':
        # If the payment method is 'stripe', create the checkout session and set the success URL
        success_url = request.build_absolute_uri(reverse('payment_success')) + f'?order_id={order.order_id}&payment_method=stripe'
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Order',
                    },
                    'unit_amount': int(order.get_total_price() * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,  # This is the URL Stripe will redirect to on success
            cancel_url=request.build_absolute_uri(reverse('checkout_page')),
        )

        # Redirect to Stripe checkout session
        return redirect(checkout_session.url)
    
    elif payment_method == 'cod':
        # If the payment method is 'COD', mark the order as complete
        order.ordered = True  # Mark the order as 'ordered'
        order.save()  # Save the order with the updated status
        print(f"Order status updated to: {order.ordered}")
        
        
        payment_success_url = reverse('payment_success') + f'?order_id={order.order_id}&payment_method=cod'
        
        
        return HttpResponseRedirect(payment_success_url)  # Use HttpResponseRedirect to perform the redirect
    
    else:
        
        messages.error(request, "Invalid payment method selected.")
        return redirect('checkout_page')

def payment_success(request):
    order_id = request.GET.get('order_id')
    payment_method = request.GET.get('payment_method', '')

    try:
        order = Order.objects.get(order_id=order_id)

        # If the order is cancelled, do not proceed with further updates
        if order.order_status == Order.CANCELLED:
            messages.error(request, "This order has been cancelled.")
            return redirect('track_order')

        # If the payment method is valid (COD or Stripe), process it.
        if payment_method in ['cod', 'stripe']:
            messages.success(request, f"Your payment was successful ({payment_method.upper()})!")

            # Ensure the order status is set to 'Pending' after payment
            if order.order_status != Order.CANCELLED:
                order.order_status = Order.PENDING  # Explicitly set to Pending

            if not order.ordered:
                order.ordered = True
                order.ordered_date = timezone.now()

            # Set order delivered and received to False after payment
            if not order.order_delivered:
                order.order_delivered = False
            if not order.order_received:
                order.order_received = False

            # Save the updated order status
            order.save()

        else:
            messages.error(request, "Unknown payment method.")

        total_amount = order.get_total_price()

        return render(request, 'core/payment_success.html', {'order': order, 'total_amount': total_amount})

    except Order.DoesNotExist:
        messages.error(request, "Order not found or payment failed.")
        return redirect('checkout_page')



@login_required
def track_order(request):
    # Fetch orders for the logged-in user, ordered by the most recent
    orders = Order.objects.filter(user=request.user).order_by('-ordered_date')

    # Force a refresh of the order data from the database to ensure you have the latest changes
    for order in orders:
        order.refresh_from_db()

    # Convert ordered_date to the local time zone if necessary
    for order in orders:
        order.ordered_date = timezone.localtime(order.ordered_date)

    return render(request, 'core/track_order.html', {'orders': orders})



def order_detail(request, order_id):
    # Get the order by its ID and user (to ensure the user can only access their own orders)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Fetch the order items associated with the order
    order_items = order.items.all()

    return render(request, 'core/order_detail.html', {
        'order': order,
        'order_items': order_items,  # Pass the order items to the template
    })

def invoice(request, order_id):
    try:
        # Fetch the order using the order ID
        order = Order.objects.get(user=request.user, order_id=order_id, ordered=True)

        # Get the checkout address that was saved with the order
        checkout_address = order.checkout_address

        if not checkout_address:
            messages.error(request, "No address found for this order.")
            return redirect('checkout_page')  # Redirect to address selection page

        return render(request, 'core/invoice.html', {
            'order': order,
            'checkout_address': checkout_address,
            'total_amount': order.get_total_price(), 
        })
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('index')


def payment_failed(request):
    messages.error(request, "Your payment failed. Please try again.")
    return redirect('payment_page')


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_dashboard')  # Redirect back to dashboard after saving
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/edit_product.html', {'form': form})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the new product to the database
            form.save()
            return redirect('custom_admin_dashboard')  # Redirect to the admin dashboard after adding product
    else:
        form = ProductForm()

    return render(request, 'core/edit_product.html', {'form': form, 'add_product': True})






@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('custom_admin_dashboard')  # Redirect back to the dashboard after deletion



def category_list(request):
    # Fetch all categories
    categories = Category.objects.all()

    # Generate category data with product count
    category_data = [
        {
            'category': category,
            'product_count': category.products.count()  # Get the count of related products
        }
        for category in categories
    ]

    # Debugging: Print the category_data
    print("Category Data:", category_data)  # This will show in the terminal

    # Render the template and pass the category data
    return render(request, 'core/category_list.html', {'category_data': category_data})




def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # If the request is POST, update the category name
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to category list after saving changes
    else:
        form = CategoryForm(instance=category)

    return render(request, 'core/edit_category.html', {'form': form, 'category': category})

# Delete Category View
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.delete()
        return redirect('category_list')  # Redirect back to category list after deleting the category

    return render(request, 'core/delete_category.html', {'category': category})


@never_cache
@login_required
def edit_banner(request, id):
    banner = get_object_or_404(Banner, id=id)  # Get the banner to edit
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)  # Pre-populate form with current banner data
        if form.is_valid():
            form.save()  # Save updated banner
            return redirect('banner_list')  # Redirect back to the banner list page
    else:
        form = BannerForm(instance=banner)  # Display form with current banner data
    
    return render(request, 'core/edit_banner.html', {'form': form, 'banner': banner})



@login_required
def recent_orders(request):
    if not request.user.is_superuser:
        return redirect('login')  # Redirect to login if the user is not a superuser

    orders = Order.objects.all()  # Fetch all orders or filter them as needed
    
    return render(request, 'core/recent_orders.html', {'orders': orders})


@login_required
def product_list(request):
    if not request.user.is_superuser:
        return redirect('login')  # Redirect to login if the user is not a superuser

    products = Product.objects.all()  # Fetch all products
    return render(request, 'core/product_list.html', {'products': products})

@never_cache
@login_required
def banner_list(request):
    if not request.user.is_superuser:
        return redirect('login')

    banners = Banner.objects.all()  # Fetch all banners (this should get the latest data)
    return render(request, 'core/banner_list.html', {'banners': banners})

@never_cache
def delete_banner(request, id):
    banner = get_object_or_404(Banner, id=id)
    banner.delete()
    return redirect('banner_list')


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new category
            return redirect('category_list')  # Redirect back to the category list
    else:
        form = CategoryForm()

    return render(request, 'core/add_category.html', {'form': form})




def products_by_category(request):
    # Get the number of products in each category
    categories = Category.objects.annotate(product_count=Count('products'))

    # Prepare the chart data
    chart_data = {
        'labels': [category.category_name for category in categories],  # Use 'category_name' from Category model
        'data': [category.product_count for category in categories]
    }

    # Convert chart_data to JSON format
    chart_data_json = json.dumps(chart_data)

    return render(request, 'core/products_by_category.html', {
        'chart_data': chart_data_json
    })



@login_required
def add_banner(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)  # Handle form submission with file upload
        if form.is_valid():
            form.save()  # Save the new banner to the database
            return redirect('banner_list')  # Redirect back to the banner list after saving
    else:
        form = BannerForm()  # Initialize an empty form on GET request
    
    return render(request, 'core/add_banner.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect('login')  # Redirect to login if the user is not a superuser

    users = User.objects.all()  # Get all users

    return render(request, 'core/user_list.html', {'users': users})





@login_required
def user_detail(request, id):
    user = get_object_or_404(User, id=id)  # Get the user or return 404 if not found
    hashed_password = user.password  # Store the hashed password
    last_login = user.last_login
    date_joined = user.date_joined

    # Handle password reset
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)  # Keep the user logged in after password change
            return redirect('user_detail', id=user.id)  # Redirect to avoid resubmitting the form
    else:
        password_form = PasswordChangeForm(user=user)

    return render(request, 'core/user_detail.html', {
        'user': user,
        'hashed_password': hashed_password,
        'last_login': last_login,
        'date_joined': date_joined,
        'password_form': password_form,
    })





def user_profile(request):
    user = request.user
    
    if request.method == 'POST':
        # Handle email update
        if 'email' in request.POST:
            email = request.POST.get('email')
            if email != user.email:
                user.email = email
                user.save()
                messages.success(request, 'Your email has been updated successfully!')
        
        # Handle password reset
        if 'password' in request.POST:
            password = request.POST.get('password')
            if password:
                # Reset the password securely
                user.set_password(password)  # This hashes the new password
                user.save()

                # Re-authenticate the user so they don't get logged out
                update_session_auth_hash(request, user)

                messages.success(request, 'Your password has been updated successfully!')

        return redirect('user_profile')  # Redirect to refresh the page

    return render(request, 'core/user_profile.html')
