from typing import Reversible
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.utils import timezone

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User,null=False,blank=False,on_delete = models.CASCADE)
    #extra fields:
    phone_field = models.CharField(max_length=12,blank=False)

    def __str__(self):
        return self.user.username
        
class OTP(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.username}"
    
class Category(models.Model):
    category_name = models.CharField(max_length=200)
    def __str__(self):
        return self.category_name
    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey('Category',on_delete=models.CASCADE,related_name='products')
    desc = models.TextField()
    price = models.FloatField(default=0.0)
    discount_price = models.FloatField(default=0.0, blank=True, null=True) 
    product_available_count = models.IntegerField(default=0)
    img = models.ImageField(upload_to='images/', blank=True, null=True)


    def get_add_to_cart_url(self):
        return Reversible("core:add-to-cart",kwargs={
            "pk":self.pk
        })
    
    def __str__(self):
        return self.name
    
    def get_discount_price(self):
        return self.discount_price if self.discount_price else self.price
    
    
class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
    
    def get_total_item_price(self):
        # Ensure the price is multiplied by the quantity
        price = self.product.discount_price if self.product.discount_price else self.product.price
        return self.quantity * price

    
    def get_final_price(self):
        return self.get_total_item_price()
    
class CheckoutAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)

    zip_code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Order(models.Model):
    PENDING = 'Pending'
    COMPLETED = 'Completed'
    PROCESSING = 'Processing'
    CANCELLED = 'Cancelled'

    ORDER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (PROCESSING, 'Processing'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('OrderItem')  # Assuming you have an OrderItem model
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    checkout_address = models.ForeignKey('CheckoutAddress', on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    datetime_ofpayement = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    order_delivered = models.BooleanField(default=False)
    order_received = models.BooleanField(default=False)
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default=PENDING,  # Ensure the default status is 'Pending'
    )

    def save(self, *args, **kwargs):
        # Ensure datetime_ofpayement is set if not already
        if not self.datetime_ofpayement:
            self.datetime_ofpayement = timezone.now()  # Get the current time in the correct timezone

        # Ensure order ID is set based on the payment datetime
        if not self.order_id:
            # Use the datetime of payment to generate a unique order ID
            self.order_id = self.datetime_ofpayement.strftime('PAY2ME%Y%m%d%H%M%S') + str(self.id or 0)

        # Ensure that the status is 'Pending' if the order is not yet marked as ordered
        if not self.ordered:
            self.order_status = self.PENDING

        # Call the parent save method to persist the order
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id} for {self.user.username}"

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_item_price()  # Assuming you have a method in OrderItem for item price
        return total

    def get_total_count(self):
        return self.items.count()



    
    

# models.py
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist item for {self.user.username} - {self.product.name}"

    # You may also want to add a unique constraint to ensure that the same product cannot be added multiple times
    class Meta:
        unique_together = ('user', 'product')



class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"

    class Meta:
        unique_together = ('product', 'user')  

class Banner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title