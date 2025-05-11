# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import ProductForm
from django.core.paginator import Paginator

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Handle search
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Pagination
    paginator = Paginator(products, 9)  # Show 9 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'shop/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query
    })


@login_required
def dashboard_orders(request):
    # Only allow staff/admin users to access dashboard
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access the dashboard.")
        return redirect('shop:product_list')

    # Get all orders with their items
    orders = Order.objects.all().order_by('-created_at')

    return render(request, 'shop/dashboard/orders.html', {
        'orders': orders
    })


@login_required
def update_order_status(request, order_id):
    # Only allow staff/admin users to update order status
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to update order status.")
        return redirect('shop:product_list')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        order.paid = True
        order.save()
        messages.success(request, f"Order #{order.id} has been marked as paid.")

    return redirect('shop:dashboard_orders')

def order_confirmation(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        # For guests, you might want to add some security check
        # For now, just get the order by ID
        order = get_object_or_404(Order, id=order_id)

    return render(request, 'shop/order_confirmation.html', {'order': order})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    related_count = related_products.count()
    if related_count < 8:
        other_products = Product.objects.filter(
            available=True
        ).exclude(
            id=product.id
        ).exclude(
            category=product.category
        )[:8-related_count]

        from itertools import chain
        recommended_products = list(chain(related_products, other_products))
    else:
        recommended_products = list(related_products[:8])

    return render(request, 'shop/product/detail.html', {
        'product': product,
        'related_products': recommended_products
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_id=session_id)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('shop:product_list')


def cart_detail(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_id=session_id)

    return render(request, 'shop/cart/detail.html', {'cart': cart})


def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    # Check if the cart belongs to the current user/session
    if request.user.is_authenticated:
        if item.cart.user != request.user:
            messages.error(request, "You cannot modify this cart.")
            return redirect('shop:cart_detail')
    else:
        if item.cart.session_id != request.session.session_key:
            messages.error(request, "You cannot modify this cart.")
            return redirect('shop:cart_detail')

    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('shop:cart_detail')


def cart_update(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    # Check if the cart belongs to the current user/session
    if request.user.is_authenticated:
        if item.cart.user != request.user:
            messages.error(request, "You cannot modify this cart.")
            return redirect('shop:cart_detail')
    else:
        if item.cart.session_id != request.session.session_key:
            messages.error(request, "You cannot modify this cart.")
            return redirect('shop:cart_detail')

    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('shop:cart_detail')


def checkout(request):
    # Cart handling remains the same
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    if request.method == 'POST':
        # Add debugging to see what's being submitted
        print("Form data received:", request.POST)

        # Improved validation with better debugging
        required_fields = ['full_name', 'email', 'address', 'postal_code', 'city', 'country']
        missing_fields = []

        for field in required_fields:
            value = request.POST.get(field, '')
            print(f"Field {field}: '{value}'")

            # Strip whitespace and check if empty
            if not value.strip():
                missing_fields.append(field.replace('_', ' ').title())

        if missing_fields:
            fields_text = ", ".join(missing_fields)
            messages.error(request, f"Please fill in these required fields: {fields_text}")

            # Return the form with the data already filled in
            return render(request, 'shop/checkout.html', {
                'cart': cart,
                'form_data': request.POST  # Pass the form data back
            })

        # Create order with form data
        order = Order(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            phone=request.POST.get('phone', '')
        )
        order.save()

        # Transfer cart items to order
        if cart.items.exists():
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # Clear the cart
            cart.items.all().delete()

            messages.success(request, "Your order has been successfully placed!")
            return redirect('shop:order_confirmation', order_id=order.id)
        else:
            messages.error(request, "Your cart is empty.")
            return redirect('shop:cart_detail')

    return render(request, 'shop/checkout.html', {'cart': cart})

def order_complete(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        # For guests, just get the order by ID
        order = get_object_or_404(Order, id=order_id)

    return render(request, 'shop/order_complete.html', {'order': order})