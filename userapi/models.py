from django.db import models
from adminapi.models import CustomUser,Bid
# Create your models here.

class Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, null=True, blank=True)
    card_number = models.CharField(max_length=19)
    card_holder = models.CharField(max_length=100)
    expiry_date = models.CharField(max_length=5)  # Stored as MM/YY
    
    # For security purposes, don't store CVV in the database
    # CVV is in the form for processing but isn't stored permanently
    
    created_at = models.DateTimeField(auto_now_add=True)
    cvv = models.CharField(max_length=3, null=True, blank=True)  # CVV is temporary
    
    def __str__(self):
        # Only show last 4 digits for security
        masked_number = "XXXX XXXX XXXX " + self.card_number[-4:] if self.card_number else "No card number"
        return f"{self.card_holder} - {masked_number}"
    
    # Method to get masked card number for display
    def get_masked_card_number(self):
        if not self.card_number:
            return "No card number"
        # Only show last 4 digits
        return "XXXX XXXX XXXX " + self.card_number[-4:]

