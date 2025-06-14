from django import forms
from  adminapi.models import Seller,Spice,Auction,Bid,Payment,Feedbacks
from django.contrib.auth.forms import UserCreationForm
from userapi.models import Card
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError



class RegForm(UserCreationForm):
    class Meta:
        model=Seller
        fields=["name","id_proof","profile","address","phone","email","username","password1","password2"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Address', 'rows': 3}),
            'phone': forms.NumberInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Phone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Email Address'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Username'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'style': 'margin-bottom: 5px;', 'placeholder': 'Reenter password'}),

        }
        
    def __init__(self, *args, **kwargs):
        super(RegForm, self).__init__(*args, **kwargs)
        # Make some fields optional if needed
        self.fields['phone'].required = False
        self.fields['address'].required = False
        self.fields['profile'].required = False
        self.fields['id_proof'].required = False
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        
        # If the email has changed, check if it's already in use by another user
        if email and Seller.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email address is already in use by another account.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # If the username has changed, check if it's already in use
        if username and Seller.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Username is already taken.')
        return username

class ProfileUpdateForm(forms.ModelForm):
    """Form for updating seller profile"""
    
    class Meta:
        model = Seller
        fields = ['name', 'username', 'email_address', 'phone', 'address', 'profile', 'id_proof']
        
    # If needed, explicitly define the email_address field to ensure it's handled correctly
    email_address = forms.EmailField(required=True)
    
    def clean_email_address(self):
        """Validate that the email is not already in use by another user"""
        email_address = self.cleaned_data.get('email_address')
        user_id = self.instance.id if self.instance else None
        
        # Check if email exists but exclude the current user
        if Seller.objects.filter(email_address=email_address).exclude(id=user_id).exists():
            raise ValidationError("Email address is already in use by another account.")
        
        return email_address
    
class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)
    
class AddProducts(forms.ModelForm):
    class Meta:
        model=Spice
        fields=["name","description","stock_quantity","image"]
        widgets={
            "name":forms.TextInput(attrs={"class":"form-control"}),
            "description":forms.Textarea(attrs={"class":"form-control","rows":3}),
            "stock_quantity":forms.NumberInput(attrs={"class":"form-control"}),
        }
            
class AddAuction(forms.ModelForm):
    class Meta:
        model=Auction
        fields=["starting_bid","expected_bid","number_of_lots","end_time"]
        widgets={
            "starting_bid":forms.NumberInput(attrs={"class":"form-control"}),
            "expected_bid":forms.NumberInput(attrs={"class":"form-control"}),
            "number_of_lots":forms.NumberInput(attrs={"class":"form-control"}),
            "end_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"})
        }
              
class AddBid(forms.ModelForm):
    class Meta:
        model=Bid
        fields=["amount"]
        widgets={
            "amount":forms.NumberInput(attrs={"class":"form-control"}),
        }
        
class AddFeedback(forms.ModelForm):

    class Meta:
        model = Feedbacks
        fields = ["rating", "comment"]
        widgets = {
                        
            'rating': forms.NumberInput(attrs={'class': 'form-control'}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

class CardForm(forms.ModelForm):
    card_number = forms.CharField(
        label='Card Number',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXXX XXXX XXXX XXXX',
            'maxlength': '19'
        }),
        required=True
    )
    card_holder = forms.CharField(
        label='Card Holder Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name as it appears on card'
        }),
        required=True
    )
    expiry_date = forms.CharField(
        label='Expiration Date',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'maxlength': '5'
        }),
        required=True
    )
    cvv = forms.CharField(
        label='CVV',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX',
            'maxlength': '4'
        }),
        required=True
    )

    class Meta:
        model = Card
        fields = ['card_number', 'card_holder', 'expiry_date', 'cvv']
        
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        # Remove spaces if any
        card_number = card_number.replace(" ", "")
        # Basic validation - check if all digits
        if not card_number.isdigit():
            raise forms.ValidationError("Card number should contain only digits")
        # Check length
        if len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError("Invalid card number length")
        return card_number
        
    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get('expiry_date')
        # Check format
        if not '/' in expiry_date:
            raise forms.ValidationError("Expiry date should be in MM/YY format")
        try:
            month, year = expiry_date.split('/')
            month = int(month)
            year = int(year)
            # Check if month is valid
            if month < 1 or month > 12:
                raise forms.ValidationError("Month should be between 1 and 12")
        except ValueError:
            raise forms.ValidationError("Expiry date should be in MM/YY format")
        return expiry_date
        
    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')
        # Check if all digits
        if not cvv.isdigit():
            raise forms.ValidationError("CVV should contain only digits")
        # Check length
        if len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError("CVV should be 3 or 4 digits")
        return cvv
    
      
