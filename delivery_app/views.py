from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone  # For the delivered today count
from django.views.generic import DetailView
from delivery_app.forms import ShippingStatusUpdateForm,ProfileUpdateForm
from django.views.generic import ListView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from adminapi.models import BidPurchase,DeliveryAgent
from django.urls import reverse_lazy



def is_delivery_agent(user):
    return user.is_authenticated and user.user_type == 'DeliveryAgent'

@login_required
@user_passes_test(is_delivery_agent)
def home(request):
    return render(request, 'delivery/home.html')

def logoutuser(request,*args,**kwargs): 
    logout(request)
    return redirect('index')

class AssignedOrdersView(LoginRequiredMixin, ListView):
    model = BidPurchase
    template_name = 'delivery/assigned_orders.html'
    context_object_name = 'assigned_orders'

    def get_queryset(self):
        return BidPurchase.objects.select_related(
            'bid__bidder', 
            'bid__auction__auctioneer'
        ).filter(
            delivery_agent=self.request.user
        ).exclude(
            shipping_status__in=['delivered', 'returned']
        ).order_by('-purchase_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add stats for the dashboard
        queryset = self.get_queryset()
        context['stats'] = {
            'processing': queryset.filter(shipping_status='processing').count(),
            'shipped': queryset.filter(shipping_status='shipped').count(),
            'delivered': BidPurchase.objects.filter(
                delivery_agent=self.request.user,
                shipping_status='delivered',
                purchase_date__date=timezone.now().date()
            ).count(),
            'returned': queryset.filter(shipping_status='returned').count(),
        }
        
        return context

class OrderDetailView(DetailView):
    model = BidPurchase
    template_name = 'delivery/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ShippingStatusUpdateForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ShippingStatusUpdateForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            return redirect('delivery_app:order_detail', pk=self.object.pk)
        else:
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

class CompletedOrdersView(LoginRequiredMixin, ListView):
    model = BidPurchase
    template_name = 'delivery/completed_orders.html'  # Update to your actual template path
    context_object_name = 'completed_orders'

    def get_queryset(self):
        return BidPurchase.objects.select_related(
            'bid__bidder',
            'bid__auction__auctioneer'
        ).filter(
            delivery_agent=self.request.user,
            shipping_status='delivered'
        ).order_by('-purchase_date')

class ProfileUpdateView(UpdateView):
    template_name = "delivery/profile.html"
    model = DeliveryAgent
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("delivery_app:profile")

    def get_object(self, queryset=None):
        """Get the DeliveryAgent object for the current user"""
        return get_object_or_404(DeliveryAgent, id=self.request.user.id)

    def form_valid(self, form):
        """Save form and redirect on success"""
        self.object = form.save()
        return redirect(self.success_url)

    def form_invalid(self, form):
        """Print errors and re-render the form"""
        print(f"Form errors: {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """Add user context to template"""
        context = super().get_context_data(**kwargs)
        context['user'] = self.object
        return context

