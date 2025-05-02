from django.shortcuts import render,redirect
from django.views import View
from adminapi.models import Seller,Spice,Bid,Auction,Payment,Feedbacks,CustomUser,BidPurchase
from django.contrib import messages
from django.views.generic import CreateView,FormView,ListView,UpdateView
from django.urls import reverse_lazy
from userapi.forms import RegForm,LoginForm,AddProducts,AddAuction,AddBid,AddFeedback,ProfileUpdateForm
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from reportlab.pdfgen import canvas
import io
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
from userapi.models import Card
from userapi.forms import CardForm
from django.core.mail import send_mail



def signin_required(fn):    
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session!..please login")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

def landingpage(request):
    return render(request,"user/index.html")
    
class SignInView(FormView):
    template_name="user/loginpage.html"
    form_class=LoginForm
    
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Get user role from CustomUser model and redirect accordingly
                try:
                    user_profile = CustomUser.objects.get(username=user.username)
                    user_type  = user_profile.user_type 
                                        
                    if user_type  == 'Admin':
                        return redirect('/adminapi/home/')
                    elif user_type  == 'Seller':
                        return redirect("auctions-list")
                    else:
                        messages.error(request, "Invalid user type.")
                        return redirect('signin')
            
                except CustomUser.DoesNotExist:
                    # Fallback if profile doesn't exist
                    return redirect('user_dashboard')
            else:
                return redirect('signin')
        else:
            return redirect('signin')

class RegView(CreateView):
    template_name = "user/register.html"
    model= Seller
    form_class = RegForm
    success_url=reverse_lazy("signin")


    def form_valid(self, form):
        form.instance.user_type = 'Seller'
        return super().form_valid(form)   
 
class ProfileUpdateView(UpdateView):
    template_name = "user/profile.html"
    model = Seller
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("profile")
    
    def get_object(self, queryset=None):
        """Get the Seller object for the current user"""
        return get_object_or_404(Seller, id=self.request.user.id)
    
    def post(self, request, *args, **kwargs):
        """Override post method to ensure data is saved"""
        self.object = self.get_object()
        
        # Debug print to see what's coming in the POST data
        print(f"POST data: {request.POST}")
        print(f"FILES data: {request.FILES}")
        
        # Get the form and populate it with the data
        form = self.form_class(request.POST, instance=self.object, files=request.FILES)
        
        if form.is_valid():
            seller = form.save()
            messages.success(request, "Profile updated successfully")
            return redirect(self.success_url)
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Profile update failed. Please check the form for errors: {form.errors}")
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()  # This ensures 'user' is available in the template
        return context

# class SignInView(FormView):
#     template_name="user/loginpage.html"
#     form_class=LoginForm
    
#     def post(self,request,*args,**kwargs):
#         form=LoginForm(request.POST)
#         if form.is_valid():
#             uname=form.cleaned_data.get("username")
#             pwd=form.cleaned_data.get("password")
#             usr=authenticate(request,username=uname,password=pwd)
#             if usr:
#                 login(request,usr)
#                 messages.success(request,"login success")
#                 return redirect("auctions-list")
#             else:
#                 messages.error(request,"failed to login")
#                 return render(request,self.template_name,{"form":form})
            
class AuctionsListView(ListView):
    model = Auction
    template_name = "user/home.html"
    context_object_name = "auctions"

    def get_queryset(self):
        """Return only available auctions."""
        return Auction.objects.filter(status='Available')

    def get_context_data(self, **kwargs):
        """Add extra context to the template."""
        # Update expired auctions before loading context
        self._update_expired_auctions()

        context = super().get_context_data(**kwargs)
        context['highestbid'] = Bid.objects.order_by('-amount').first()
        context['time'] = timezone.now()
        return context

    def _update_expired_auctions(self):
        """Update expired auctions and notify winners."""
        expired_auctions = Auction.objects.filter(
            end_time__lte=timezone.now(),
            status='Available'
        )

        for auction in expired_auctions:
            self._finalize_auction(auction)

    def _finalize_auction(self, auction):
        """Mark auction as sold and notify the highest bidder."""
        auction.status = 'Sold'
        auction.save()

        # Update related spice status
        auction.spice.status = 'Not Available'
        auction.spice.save()

        print("Auction marked as sold:", auction)

        # Select highest bid
        highest_bid = auction.bid_set.order_by('-amount').first()
        if highest_bid:
            highest_bid.is_selected = True
            highest_bid.save()

            # Notify the winning bidder
            self._notify_bid_winner(highest_bid)

    def _notify_bid_winner(self, bid):
        """Send email to the winning bidder."""
        user_email = bid.bidder.email_address
        print("Sending email to winner:", user_email)

        subject = "Spices Auction!"
        message = (
            f"Dear Customer,\n\n"
            "You have won the Bid! "
            "We're thrilled to announce you as the winner.\n\n"
            "Feel free to explore our website and discover a world of exciting products and services tailored just for you.\n\n"
            "If you have any questions or need assistance, don't hesitate to reach out to us.\n\n"
            "Best regards,\n"
            "Spices Auction Board"
        )
        send_mail(subject, message, "spicesauction11@gmail.com", [user_email])

def bids_list_view(request):
    user_id = request.user.id
    bids = Bid.objects.filter(auction__auctioneer_id=user_id)
    cards = Card.objects.filter(user=user_id)
    
    # Get all bid purchases related to these bids
    bid_purchases = BidPurchase.objects.filter(bid__in=bids)
    
    # Create a dictionary to map bid IDs to their payment status
    payment_status_by_bid = {purchase.bid.id: purchase.payment_status for purchase in bid_purchases}
    
    # Add payment status to each bid object
    for bid in bids:
        bid.payment_status = payment_status_by_bid.get(bid.id, None)
    
    context = {
        'bids': bids,
        'cards': cards,
    }
    
    return render(request, 'user/bids.html', context)

def delete_bid_view(request, bid_id):
    try:
        # Get the bid
        bid = Bid.objects.get(id=bid_id, auction__auctioneer_id=request.user.id)
        
        # Check if user has permission to delete (they must be the auctioneer)
        if bid.auction.auctioneer_id != request.user.id:
            messages.error(request, "You don't have permission to delete this bid.")
            return redirect('bid-list')
        
        # Delete the bid
        bid.delete()
        messages.success(request, "Bid deleted successfully.")
    except Bid.DoesNotExist:
        messages.error(request, "Bid not found.")
    
    return redirect('bid-list')
    
class ProductsListView(ListView):
    template_name="user/products.html"
    form_class=AddProducts
    model=Spice
    context_object_name="spices"
    
    def get_queryset(self):
        user_id = self.request.user.id
        return Spice.objects.filter(seller=user_id)
    
class ProductsAddView(CreateView):
    template_name="user/addproducts.html"
    form_class=AddProducts
    model=Spice
    success_url=reverse_lazy("products-list")

    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        form.instance.seller = seller_instance
        messages.success(self.request, "Product added successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Product adding failed")
        return super().form_invalid(form)
    
def remove_product(request,*args,**kwargs):
    id=kwargs.get("pk")
    Spice.objects.filter(id=id).delete()
    return redirect("products-list") 

class AuctionAddView(CreateView):
    template_name="user/addauction.html"
    form_class=AddAuction
    model=Auction
    success_url=reverse_lazy("products-list")

  # In AuctionAddView
    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        id=self.kwargs.get("pk")
        spice=Spice.objects.get(id=id)
        form.instance.auctioneer = seller_instance
        form.instance.spice = spice
        form.instance.status = 'Available'  # Explicitly set status to Available
        messages.success(self.request, "Auction added successfully")
        auction = super().form_valid(form)
        print(f"New auction created: {form.instance}, Status: {form.instance.status}")
        return auction

    
    def form_invalid(self, form):
        messages.error(self.request, "Auction adding failed")
        return super().form_invalid(form)
    
from django.db.models import Max

class place_bid(CreateView):
    template_name="user/addbid.html"
    form_class=AddBid
    model=Bid
    success_url=reverse_lazy("auctions-list")

    def form_valid(self, form):
        auction_id = self.kwargs.get("pk")
        auction = get_object_or_404(Auction, id=auction_id)
        bidder_id = self.request.user.id
        
        # Check if the bidder is the owner of the product
        if auction.auctioneer.id == bidder_id:
            messages.error(self.request, "You cannot bid on your own product")
            return redirect("auctions-list")
        
        amount = form.cleaned_data.get('amount')
        bidder = get_object_or_404(Seller, id=bidder_id)
        form.instance.auction = auction
        form.instance.bidder = bidder 
        bid = form.save() 
        
        messages.success(self.request, "Bid placed successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Bid adding failed")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auction_id = self.kwargs.get("pk")
        auction = get_object_or_404(Auction, id=auction_id)
        context['auction'] = auction
        high_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()
        if high_bid:
            context['highbid'] = high_bid.amount
        else:
            context['highbid'] = None
    
        return context
    
def wonbids_view(request):
    user_id = request.user.id
    bids = Bid.objects.filter(bidder=user_id, is_selected=True)
    cards = Card.objects.filter(user=user_id)
    
    # Check for bids that are selected but don't have corresponding purchases
    for bid in bids:
        # Try to find an existing purchase for this bid
        existing_purchase = BidPurchase.objects.filter(bid=bid).first()
        
        # If no purchase exists, create one
        if not existing_purchase:
            new_purchase = BidPurchase(
                bid=bid,
                amount_paid=bid.amount,  # Assuming Bid model has an amount field
            )
            new_purchase.save()
    
    # Get all payments after potentially creating new ones
    payments = BidPurchase.objects.filter(bid__bidder=user_id, bid__is_selected=True)
    
    # Create a dictionary to easily access payment status by bid
    payment_status_by_bid = {payment.bid.id: payment.payment_status for payment in payments}
    
    # Add payment status to bids for template use
    for bid in bids:
        bid.payment_status = payment_status_by_bid.get(bid.id, 'pending')
    
    context = {
        'bids': bids,
        'cards': cards,
        'payments': payments,
    }
    
    return render(request, 'user/wonbids.html', context)
       
import json
from django.http import JsonResponse

def create_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        buyer_id = data.get('buyer_id')
        bid_id = data.get('bid_id')

        print("Data received from front end:", data)

        try:
            payment = Payment.objects.create(
                user_id=buyer_id,
                bid_id=bid_id,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

    # return redirect('payment_success')

def download_bill(request, bid_id):
    bid = Bid.objects.get(id=bid_id)
    spice_name = bid.auction.spice.name
    unitprice = bid.amount
    user_name = bid.bidder.seller.name
    date=timezone.now()
    quantity=bid.auction.spice.stock_quantity
    amount=unitprice*quantity
    auction=bid.auction.auctioneer
    

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Spice Auction Bill")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Thank you for purchasing {spice_name} from our site.")
    p.drawString(100, 700, f"Auctioneer : {auction}")
    p.drawString(100, 680, f"User: {user_name}")
    p.drawString(100, 660, f"Date: {date}")
    p.drawString(100, 640, f"Quantity: {quantity}")
    p.drawString(100, 620, f"Unit Price: {unitprice}")
    p.drawString(100, 580, f"___________________________________")
    p.drawString(100, 550, f"Total Price: Rs. {amount}")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spice_auction_bill.pdf"'

    return response

def download_slip(request, bid_id):
    bid = Bid.objects.get(id=bid_id)
    spice_name = bid.auction.spice.name
    unitprice = bid.amount
    date=timezone.now()
    quantity=bid.auction.spice.stock_quantity
    amount=unitprice*quantity
    user_name = bid.bidder.seller.name

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Spice Auction Bill.. payment slip")
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Spice: {spice_name}")
    p.drawString(100, 700, f"Unit Price: Rs. {unitprice}")
    p.drawString(100, 680, f"Quantity: {quantity} kg")
    p.drawString(100, 660, f"User: {user_name}")
    p.drawString(100, 640, f"Total amount: Rs. {amount}")
    p.drawString(100, 600, f"Payment Date: {date}")
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="spice_auction_bill.pdf"'

    return response
      
class AddfeedbackView(CreateView):
    template_name="user/feedback.html"
    form_class=AddFeedback
    model=Feedbacks
    success_url=reverse_lazy("auctions-list")
 
 
    def form_valid(self, form):
        seller_instance = get_object_or_404(Seller, pk=self.request.user.id)
        form.instance.user = seller_instance
        messages.success(self.request, "Feedback added successfully")
        return super().form_valid(form)

    
    def form_invalid(self, form):
        messages.error(self.request, "Feedback adding failed")
        return super().form_invalid(form)

def logoutuser(request,*args,**kwargs): 
    logout(request)
    return redirect('index')

def card_input(request, bid_id):
    user = request.user
    
    # Find the specific booking
    bid = get_object_or_404(Bid, id=bid_id)

    payment = get_object_or_404(BidPurchase, bid=bid)

    

    if payment.payment_status == 'completed':
        messages.error(request, "Payment already completed.")
        
        return redirect('payment_success')
    
       
    if request.method == 'POST':
        form = CardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = user
            card.bid = bid
            card.save()
            bid.bid_status = True
            bid.save()
            payment.payment_status = 'completed'
            payment.save()
   
            return redirect('payment_success')
    else:
        # For GET requests, create an empty form
        form = CardForm()
        
    context = {
        'bid': bid,
        'form': form
        
    }

    return render(request, 'user/card_input.html', context)

def payment_success(request):
    return render(request, 'user/success.html') 

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from .models import CustomUser 

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Prepare email
            subject = 'Password Reset Request'
            email_template = 'user/reset_password_email.html'
            email_context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'TRAVELIX',
            }
            
            html_message = render_to_string(email_template, email_context)
            plain_message = f"Hi {user.username}, click this link to reset your password: {reset_url}"
            
            # Send email
            send_mail(
                subject,
                plain_message,
                'noreply@yourwebsite.com',
                [email],
                html_message=html_message,
                fail_silently=False
            )
            
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('signin')
            
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with that email address.")
    
    return render(request, 'user/forgot_password.html')

def password_reset_confirm(request, uidb64, token):
    try:
        # Decode the user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        # Verify token
        if not default_token_generator.check_token(user, token):
            messages.error(request, "Password reset link is invalid or has expired.")
            return redirect('forgot_password')
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != password2:
                messages.error(request, "Passwords don't match.")
                return render(request, 'user/password_reset_confirm.html')
            
            # Set new password
            user.set_password(password1)
            user.save()
            
            messages.success(request, "Password has been reset successfully. You can now log in with your new password.")
            return redirect('signin')
            
        return render(request, 'user/password_reset_confirm.html')
        
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        messages.error(request, "Password reset link is invalid.")
        return redirect('forgot_password')
   














