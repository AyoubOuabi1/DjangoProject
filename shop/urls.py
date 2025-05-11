# shop/urls.py
from django.urls import path
from . import views, dashboard_views

app_name = 'shop'

urlpatterns = [
    # Product URLs
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='cart_add'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),

    # Dashboard URLs
    path('dashboard/', dashboard_views.dashboard_home, name='dashboard'),

    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    # Category URLs
    path('dashboard/categories/', dashboard_views.CategoryListView.as_view(), name='dashboard_categories'),
    path('dashboard/categories/add/', dashboard_views.CategoryCreateView.as_view(), name='dashboard_category_add'),
    path('dashboard/categories/<int:pk>/edit/', dashboard_views.CategoryUpdateView.as_view(), name='dashboard_category_edit'),
    path('dashboard/categories/<int:pk>/delete/', dashboard_views.CategoryDeleteView.as_view(), name='dashboard_category_delete'),

    # Product URLs
    path('dashboard/products/', dashboard_views.ProductListView.as_view(), name='dashboard_products'),
    path('dashboard/products/add/', dashboard_views.ProductCreateView.as_view(), name='dashboard_product_add'),
    path('dashboard/products/<int:pk>/edit/', dashboard_views.ProductUpdateView.as_view(), name='dashboard_product_edit'),
    path('dashboard/products/<int:pk>/delete/', dashboard_views.ProductDeleteView.as_view(), name='dashboard_product_delete'),


]