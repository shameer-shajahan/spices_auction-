from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView,View,TemplateView,ListView,UpdateView,DetailView
from django.contrib.auth import authenticate, login,logout
from django.utils.decorators import method_decorator
from django.db.models import Count
from datetime import date
from django.db.models import Sum
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from adminapi.models import Spice,Seller,Bid,Feedbacks,Auction,Payment,DeliveryAgent


def signin_required(fn):    
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,"invalid session!..please login")
            return redirect("signin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

def is_admin(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_superuser:
            messages.error(request,"Permission denied for current user !")
            return redirect("adminsignin")
        else:
            return fn(request,*args,**kwargs)
    return wrapper

decs=[signin_required,is_admin]


class SignInView(View):
    template_name="login.html"
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    
    def post(self, request, *args, **kwargs):
        uname = request.POST.get("username")
        pwd = request.POST.get("password")
        if uname and pwd:
            usr = authenticate(request, username=uname, password=pwd)
            if usr is not None:
                login(request, usr)
                messages.success(request, "Login success")
                return redirect("home")
        
        messages.error(request, "Failed to login")
        return render(request, self.template_name)

from .forms import DeliveryAgentForm
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and user.user_type == 'Admin'

@login_required
@user_passes_test(is_admin)
def create_delivery_agent(request):
    if request.method == 'POST':
        form = DeliveryAgentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('delivery_agent_list')  # Create this view if needed
    else:
        form = DeliveryAgentForm()
    return render(request, 'delivery/create_delivery_agent.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delivery_agent_list(request):
    agents = DeliveryAgent.objects.all()
    return render(request, 'delivery/delivery_agent_list.html', {'agents': agents})

@login_required
@user_passes_test(is_admin)
def edit_delivery_agent(request, pk):
    agent = get_object_or_404(DeliveryAgent, pk=pk)
    form = DeliveryAgentForm(request.POST or None, request.FILES or None, instance=agent)
    
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('delivery_agent_list')
    
    return render(request, 'delivery/edit_delivery_agent.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def delete_delivery_agent(request, pk):
    agent = get_object_or_404(DeliveryAgent, pk=pk)
    if request.method == 'POST':
        agent.delete()
        return redirect('delivery_agent_list')
    return render(request, 'delivery/delete_delivery_agent.html', {'agent': agent})



from django.utils import timezone
  

@method_decorator(decs,name="dispatch")   
class HomeView(ListView):
    template_name = "home.html"
    model = Bid
    context_object_name = "bids" 
    
    def get_queryset(self):
        today = timezone.now().date()
        return Bid.objects.filter(timestamp__date=today)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bids_count'] = Bid.objects.aggregate(count=Count('id'))['count']
        total_amount = Payment.objects.aggregate(total_amount=Sum('bid__amount'))['total_amount'] or 0
        context['total_money']=total_amount
        today = date.today()
        context['todays_bids_count'] = Bid.objects.filter(timestamp__date=today).count()
        context['users_count'] = Seller.objects.all().count()
        return context 
    
@method_decorator(decs,name="dispatch") 
class BidsView(ListView):
    template_name="bids.html"
    model=Bid
    context_object_name="bids"    

@method_decorator(decs,name="dispatch") 
class BidDeleteView(DeleteView):
    model = Bid
    template_name = 'bid_confirm_delete.html'
    success_url = reverse_lazy('bids') 

@method_decorator(decs,name="dispatch") 
class ProductsView(ListView):
    template_name="products.html"
    model=Spice
    context_object_name="spices"
    
@method_decorator(decs,name="dispatch") 
class SpiceDeleteView(DeleteView):
    model = Spice
    template_name = 'spice_confirm_delete.html'
    success_url = reverse_lazy('products')  
   
@method_decorator(decs,name="dispatch") 
class AuctionsView(ListView):
    template_name="auctions.html"
    model=Auction
    context_object_name="auctions"
    
@method_decorator(decs,name="dispatch") 
class AuctionDeleteView(DeleteView):
    model = Auction
    template_name = 'auction_confirm_delete.html'
    success_url = reverse_lazy('auctions') 

@method_decorator(decs,name="dispatch") 
class CustomerView(ListView):
    template_name="customers.html"
    model=Seller
    context_object_name="sellers"

@method_decorator(decs,name="dispatch") 
class SellerDeleteView(DeleteView):
    model = Seller
    template_name = 'seller_confirm_delete.html'
    success_url = reverse_lazy('sellers')
    
@method_decorator(decs,name="dispatch") 
class PaymentsView(ListView):
    template_name="payments.html"
    model=Payment
    context_object_name="payments"
     
@method_decorator(decs,name="dispatch") 
class FeedbacksView(ListView):
    template_name="feedbacks.html"
    model=Feedbacks
    context_object_name="feedbacks"     
     
def signoutview(request,*args,**kwargs):
    logout(request)
    return redirect("index")


from django.views.generic import ListView
from .models import BidPurchase

class CompletedPaymentsView(ListView):
    model = BidPurchase
    template_name = 'completed_payments.html'  # Update as per your template location
    context_object_name = 'completed_purchases'

    def get_queryset(self):
        return BidPurchase.objects.filter(payment_status='completed')
    


# views.py
from django.shortcuts import get_object_or_404, redirect, render
from .models import BidPurchase
from .forms import AssignDeliveryAgentForm

def assign_delivery_agent(request, purchase_id):
    purchase = get_object_or_404(BidPurchase, id=purchase_id)
    
    if request.method == 'POST':
        form = AssignDeliveryAgentForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            return redirect('completed_payments')  # Or your list view name
    else:
        form = AssignDeliveryAgentForm(instance=purchase)

    return render(request, 'assign_delivery.html', {'form': form, 'purchase': purchase})
