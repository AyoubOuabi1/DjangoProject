# shop/dashboard_views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Category, Product, Order
from .forms import CategoryForm, ProductForm
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

# shop/dashboard_views.py
@login_required
def dashboard_home(request):
    # Basic counts
    products_count = Product.objects.count()
    categories_count = Category.objects.count()

    # Assuming you have an Order model
    orders_count = Order.objects.count()

    # Recent orders (last 7 days) - Fix using created_at instead of created
    last_week = timezone.now() - timedelta(days=7)
    recent_orders = Order.objects.filter(created_at__gte=last_week).count()

    # Revenue statistics
    # Note: The error suggests your Order model might not have a 'total' field
    # Let's check if we can calculate it from related items
    try:
        # If you have OrderItem model with product price and quantity
        from django.db.models import F, Sum
        total_revenue = Order.objects.filter(paid=True).aggregate(
            total=Sum(F('items__price') * F('items__quantity'))
        )['total'] or 0
    except:
        # Fallback to 0 if the calculation fails
        total_revenue = 0

    # Products statistics - Adjust based on your actual model relationships
    # Assuming you have OrderItem with a foreign key to Product
    top_products = Product.objects.annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]

    # Average order value - similarly calculate if structure allows
    try:
        avg_order = Order.objects.filter(paid=True).aggregate(
            avg=Sum(F('items__price') * F('items__quantity')) / Count('id', distinct=True)
        )['avg'] or 0
    except:
        avg_order = 0

    return render(request, 'shop/dashboard/home.html', {
        'products_count': products_count,
        'categories_count': categories_count,
        'orders_count': orders_count,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'top_products': top_products,
        'avg_order': avg_order,
    })

# Category Views
class CategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Category
    template_name = 'shop/dashboard/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/dashboard/category_form.html'
    success_url = reverse_lazy('shop:dashboard_categories')

class CategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'shop/dashboard/category_form.html'
    success_url = reverse_lazy('shop:dashboard_categories')

class CategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Category
    template_name = 'shop/dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('shop:dashboard_categories')

# Product Views
class ProductListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Product
    template_name = 'shop/dashboard/product_list.html'
    context_object_name = 'products'

class ProductCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/dashboard/product_form.html'
    success_url = reverse_lazy('shop:dashboard_products')

class ProductUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/dashboard/product_form.html'
    success_url = reverse_lazy('shop:dashboard_products')

class ProductDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Product
    template_name = 'shop/dashboard/product_confirm_delete.html'
    success_url = reverse_lazy('shop:dashboard_products')