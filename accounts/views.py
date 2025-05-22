from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from core.models import *
from django.contrib.auth import authenticate,login,logout
import random,string
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

# Create your views here.


def generate_otp():
    return ''.join(random.choices(string.digits,k=6))

def send_otp_email(email,otp):
    subject = "Your OTP for Registration"
    message = f"Your OTP code is: {otp}"
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])

def user_register(request):
    if request.method=="POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone = request.POST.get('phone_field')
        # print(username,email)
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username Already Exists!")
                return redirect('user_register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request,"Email Already Exists!")
                    return redirect('user_register')
                else:
                    user=User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    otp = generate_otp()
                    expiration_time = datetime.now() + timedelta(minutes=5)  # OTP valid for 5 minutes
                    otp_instance = OTP.objects.create(user=user, otp=otp, expiration_time=expiration_time)
                    otp_instance.save()
                    send_otp_email(email, otp)
                    request.session['email'] = email
                    return redirect('verify_otp')
                
                    # our_user = authenticate(username=username,password=password)
                    # if our_user is not None:
                    #  login(requset,user)
                    #  return redirect('/')
        else:
            messages.info(request,"Password and Confirm Password Mismatch!")
            return redirect('user_register')
    return render(request,'accounts/register.html')


def verify_otp(request):
    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        email = request.session.get('email')
        if not email:
            messages.error(request, "Email not found. Please register first.")
            return redirect('user_register')
        try:
            user = User.objects.get(email=email)
            otp_instance = OTP.objects.get(user=user)

            if otp_instance.expiration_time < timezone.now():
                messages.error(request, "OTP has expired. Please request a new one.")
                return redirect('verify_otp')
            if otp_entered == otp_instance.otp:
                login(request, user)
                return redirect('account_created')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")
            return redirect('user_register')
        except OTP.DoesNotExist:
            messages.error(request, "No OTP found for this user. Please request a new one.")
            return redirect('user_register')
    return render(request, 'accounts/verify_otp.html')


def account_created(request):
     if not request.user.is_authenticated:
        return redirect('user_login')
     return render(request, 'accounts/account_created.html')


def user_login(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/')
        messages.info(request,"Login Failed! Please Check Credentials")
    return render(request,'accounts/login.html')



def user_logout(request):
    logout(request)
    return redirect('/')