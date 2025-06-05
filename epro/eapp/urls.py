from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .import views
urlpatterns = [
   path('', views.firstpage, name='firstpage'),
   path('forgotpassword',views.getusername,name='forgotpassword'),
   path('verifyotp',views.verifyotp,name='verifyotp'),  
   path('passwordreset',views.passwordreset,name='passwordreset'),
   path('userlogin',views.userlogin,name="userlogin"),
   path('usersignup',views.usersignup,name="usersignup"),
   path('product/<int:id>',views.product,name='product'),
   path('review',views.review,name='review'),
   path('aboutus',views.aboutus,name='aboutus'),
   path('adminpage',views.adminpage,name='adminpage'),
   path('logout',views.logoutuser,name="logout"),
   path('add',views.add,name='add'),
   path('index',views.index,name='index'),
   path('deletion/<int:id>',views.delete_g,name='deletion'),
   path('edit_g/<int:id>',views.edit_g,name='edit_g'),
   path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
   path('cart/', views.cart_view, name='cart_view'),
   path('dele/<int:id>/', views.delete_cart, name='dele'),
   path('checkout/', views.checkout, name='checkout'),
   path('cart/increment/<int:id>/', views.increment_cart, name='increment_cart'),
   path('cart/decrement/<int:id>/', views.decrement_cart, name='decrement_cart'),
   path('sample',views.sample,name='sample'),
   path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
   path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
  #  path('search/', views.search_results, name='search_results'),
  #  path('search/', views.search_func, name='search_results'),
  path('search/', views.search_func, name='search_results'),
   path('update_order/<int:order_id>/',views.update_order_status, name='update_order'),
   path('users/', views.admin_users, name='admin_users'),
   path('orders/', views.admin_orders, name='admin_orders'),
   path('allproducts/', views.allproducts, name='allproducts'),
   path('order-success/', views.order_success, name='order_success'),
   path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
   path('add_review/<int:product_id>/', views.addReview, name='addReview'),
   path('review/<int:pk>/', views.addReview, name='addReview'),
  
   
   
   
   
   
   path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
   
   
   
   
   
   path('profile/', views.profile_view, name='profile'),
    path('profile/address/add/', views.add_address, name='add_address'),
    path('profile/address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('profile/address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('profile/edit-email/', views.edit_email, name='edit_email'),
    path('edit_username/', views.edit_username, name='edit_username'),
    path('password/change/', views.change_password, name='change_password'),  
   #  path('my-profile/', views.my_profile, name='my_profile'),  # User Profile page
   #  path('logout/', views.logout_view, name='logout'),  # User Logout page
   # path('users',views.usres_g,name='usersview'),
   
   
   # path('order/', views.order_payment, name='order_payment'),
   # path('razorpay/callback/', views.callback, name='callback'),
   
   
   
   
  path('order_payment/<int:id>/', views.order_payment, name='order_payment'),
    path('razorpay/callback/', views.callback, name='callback'),
    path('order-success/', views.order_success, name='order_success'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    
    
   path('razorpay/payment/', views.order_payment1, name='order_payment1'),
    path('razorpay/callback1/', views.callback_cart1, name='razorpay_callback'),  # Updated to callback_cart1
    # Ensure no path like 'razorpay/callback/' exists
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)