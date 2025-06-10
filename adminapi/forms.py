from django import forms
from adminapi.models import DeliveryAgent  # adjust if your models are in a different app

class DeliveryAgentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = DeliveryAgent
        fields = ['username', 'name', 'email_address', 'phone', 'vehicle_number', 'license_copy', 'profile', 'is_available', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'DeliveryAgent'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

# forms.py
from django import forms
from adminapi.models import DeliveryAgent
from .models import BidPurchase

class AssignDeliveryAgentForm(forms.ModelForm):
    class Meta:
        model = BidPurchase
        fields = ['delivery_agent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available agents
        self.fields['delivery_agent'].queryset = DeliveryAgent.objects.filter(is_available=True)


