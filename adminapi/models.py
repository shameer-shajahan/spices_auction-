from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    user_type_choices = [ 
        ('Admin', 'Admin'),
        ('Seller', 'Seller'),
        ('DeliveryAgent', 'Delivery Agent'),
    ]
    user_type = models.CharField(max_length=50, choices=user_type_choices, default='Admin') 
    email = models.EmailField(null=True)

class SuperAdmin(CustomUser):
    phone = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

class Seller(CustomUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email_address = models.EmailField()
    address = models.CharField(max_length=100)
    id_proof = models.FileField(null=True, upload_to="images",blank=True)
    profile = models.ImageField(upload_to="images", null=True, blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DeliveryAgent(CustomUser):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email_address = models.EmailField()
    vehicle_number = models.CharField(max_length=100, null=True, blank=True)
    license_copy = models.FileField(upload_to="images", null=True, blank=True)
    profile = models.ImageField(upload_to="images", null=True, blank=True)
    is_available = models.BooleanField(default=True)
    address = models.TextField(null=True, blank=True)  # Optional
    id_proof = models.FileField(upload_to="documents", null=True, blank=True)  # Optional

    def __str__(self):
        return self.name

class Spice(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="images", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    choices= [ 
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    status=models.CharField(max_length=50, choices=choices, default='Available')

    def __str__(self):
        return self.name 

class Auction(models.Model):
    spice = models.ForeignKey(Spice, on_delete=models.CASCADE)
    auctioneer = models.ForeignKey(Seller, on_delete=models.CASCADE)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    expected_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    number_of_lots = models.IntegerField(default=1)
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    choices= [ 
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Expired', 'Expired'),
    ]
    status=models.CharField(max_length=50, choices=choices, default='Available')

    def __str__(self):
        return self.spice.name

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_selected=models.BooleanField(default=False)

    def __str__(self):
        return f"Bid of {self.amount} by {self.bidder.username}"

class Payment(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    user = models.ForeignKey(Seller, on_delete=models.CASCADE)
    payment_mode=models.CharField(max_length=50,default='Online')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("completed", "Completed")], default="pending")

class Feedbacks(models.Model):
    user = models.ForeignKey(Seller, on_delete=models.CASCADE)
    rating=models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.CharField(max_length=300)
    posted_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"feedback {self.comment} by {self.user}"

class BidPurchase(models.Model):
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ], 
        default='pending'
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('online_wallet', 'Online Wallet'),
            ('other', 'Other')
        ],
        default='credit_card'
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    shipping_status = models.CharField(
        max_length=20,
        choices=[
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('returned', 'Returned')
        ],
        default='processing'
    )
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    delivery_agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Purchase for bid #{self.bid.id} - {self.bid.amount} by {self.bid.bidder.username}"