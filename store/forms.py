from django import forms

from store.models import Order, CustomUser

from django.contrib.auth.forms import UserCreationForm

class OrderForm(forms.ModelForm):
    
    class Meta:
        
        model=Order
        
        fields=['address','phone','payment_method']
        
        