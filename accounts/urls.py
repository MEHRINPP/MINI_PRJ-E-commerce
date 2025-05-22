from django.urls import path
from accounts import views
urlpatterns = [
    path('login/',views.user_login,name='user_login'),
    path('user_register/',views.user_register,name='user_register'),
    path('user_logout/',views.user_logout,name='user_logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('account-created/', views.account_created, name='account_created'),
]