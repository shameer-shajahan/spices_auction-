from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    order_id = models.CharField(max_length=100, unique=True)
    seller = models.ForeignKey(User, related_name='deliveries_made', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='deliveries_received', on_delete=models.CASCADE)
    delivery_address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_agent = models.CharField(max_length=100, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.order_id} - {self.status}"
