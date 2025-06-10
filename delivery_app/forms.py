from django import forms
from .models import Delivery
from adminapi.models import DeliveryAgent
from django.core.exceptions import ValidationError


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['order_id', 'seller', 'buyer', 'delivery_address', 'status', 'assigned_agent', 'delivery_date']


# delivery/forms.py

from django import forms
from adminapi.models import BidPurchase

class ShippingStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = BidPurchase
        fields = ['shipping_status']
        widgets = {
            'shipping_status': forms.Select(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating delivery agent profile"""

    email_address = forms.EmailField(required=True)

    class Meta:
        model = DeliveryAgent
        fields = ['name', 'email_address', 'phone', 'address', 'profile', 'id_proof', 'vehicle_number', 'license_copy']

    def clean_email_address(self):
        """Validate that the email is not already in use by another user"""
        email_address = self.cleaned_data.get('email_address')
        user_id = self.instance.id if self.instance else None

        if DeliveryAgent.objects.filter(email_address=email_address).exclude(id=user_id).exists():
            raise ValidationError("Email address is already in use by another account.")

        return email_address

