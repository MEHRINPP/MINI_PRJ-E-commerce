from django.urls import path
from core import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('custom-admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('product_list/', views.product_list, name='product_list'),
    path('add_product', views.add_product, name='add_product'),
    path('product_desc/<pk>', views.product_desc, name='product_desc'),
    path('add_to_cart/<pk>', views.add_to_cart, name='add_to_cart'),
    path('orderlist', views.orderlist, name='orderlist'),
    path('add_item/int:<pk>', views.add_item, name='add_item'),
    path('remove_item/int:<pk>', views.remove_item, name='remove_item'),
    path('add-to-wishlist/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('product/<int:pk>/reviews/', views.product_reviews, name='product_reviews'),
    path('product/<int:pk>/submit_review/', views.submit_review, name='submit_review'),
    path('checkout_page', views.checkout_page, name='checkout_page'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/select_address/', views.select_existing_address, name='select_existing_address'),
    path('payment-option/', views.payment_option, name='payment_option'),
    path('payment-redirect/<str:payment_method>/', views.payment_redirect, name='payment_redirect'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('track-order/', views.track_order, name='track_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('invoice/<str:order_id>/', views.invoice, name='invoice'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Corrected paths for category edit and delete
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    
    path('category_list/', views.category_list, name='category_list'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_banner/<int:id>/', views.edit_banner, name='edit_banner'),
    path('custom_login/', views.custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('add_category/', views.add_category, name='add_category'),
    path('recent-orders/', views.recent_orders, name='recent_orders'),
    path('banner_list', views.banner_list, name='banner_list'),
    path('banner/delete/<int:id>/', views.delete_banner, name='delete_banner'),
    path('products_by_category/', views.products_by_category, name='products_by_category'),
    path('add_banner/', views.add_banner, name='add_banner'),
    path('users/', views.user_list, name='user_list'),
    path('user/<int:id>/', views.user_detail, name='user_detail'), 
    path('profile/', views.user_profile, name='user_profile'), 

]

