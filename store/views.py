from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView, FormView
import razorpay
from store.forms import OrderForm
from store.models import BasketItem, OrderItem, Spice, ProcessingType, CustomUser, Order, Basket
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.

class SpiceListView(View):
    
    template_name = "index.html"
    
    def get(self, request, *args, **kwargs):
        print("SpiceListView is called!") 
        
        qs = Spice.objects.all()
        
        p = Paginator(qs, 4)
        
        page_number = request.GET.get('page')
        
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        context = {'page_obj': page_obj}
            
        return render(request, self.template_name, context)

class SpiceDetailView(View):
    template_name = "spice-detail.html"
    
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        qs = Spice.objects.get(id=id)
        
        return render(request, self.template_name, {"data": qs})
        
class AddtoCartView(View):
        
    def post(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        
        quantity = request.POST.get("quantity")
        
        spice_object = Spice.objects.get(id=id)
        
       
        
        if not hasattr(request.user, 'cart'):
            new_cart = Basket.objects.create(user=request.user)
            # Refresh the user instance to make sure the relationship is updated
            request.user.refresh_from_db()
        basket_object = request.user.cart
        
        BasketItem.objects.create(
            spice_object=spice_object,
            quantity=quantity,
            basket_object=basket_object,
        )
        print("item added")
        
        return redirect('store:cart-summary')  
        
class CartSummaryView(View):
    template_name = "cart_summary.html"
    
    def get(self, request, *args, **kwargs):
        
        if not hasattr(request.user, 'cart'):
            # Create a new cart for this user
            new_cart = Basket.objects.create(user=request.user)
            # Refresh the user instance to make sure the relationship is updated
            request.user.refresh_from_db()
        
        qs = BasketItem.objects.filter(basket_object=request.user.cart, is_order_placed=False)
        
        basket_item_count = qs.count()
        
        basket_total = sum([bi.item_total for bi in qs])
        
        return render(request, self.template_name, {"basket_items": qs, "basket_total": basket_total, "basket_item_count": basket_item_count})
            
class DeleteCartItemView(View):
        
    def get(self, request, *args, **kwargs):
        
        id = kwargs.get("pk")
        
        BasketItem.objects.get(id=id).delete()
        messages.success(request, "Item removed")
        return redirect("store:cart-summary")
            
class PlaceHolderView(View):
    
    template_name = "place_order.html"
    
    form_class = OrderForm
    def get(self, request, *args, **kwargs):
        
        form_instance = self.form_class()
        
        qs = request.user.cart.cart_item.filter(is_order_placed=False)
        
        total = sum([bi.item_total for bi in qs])
        
        return render(request, self.template_name, {"form": form_instance, "items": qs, "total": total})
    
    def post(self, request, *args, **kwargs):
        
        form_data = request.POST
        
        form_instance = self.form_class(form_data)
        
        if form_instance.is_valid():
            
            form_instance.instance.customer = request.user
            
            order_instance = form_instance.save()
            
            basket_items = request.user.cart.cart_item.filter(is_order_placed=False)
            
            payment_method = form_instance.cleaned_data.get("payment_method")         
            print(payment_method)
            
            for bi in basket_items:
                
                OrderItem.objects.create(
                    order_object=order_instance,
                    spice_object=bi.spice_object,
                    quantity=bi.quantity,
                    price=bi.spice_object.price   
                )
                
                bi.is_order_placed = True
                
                bi.save()

            if payment_method == "ONLINE":
                
                client = razorpay.Client(auth=("RZP_KEY_ID", "RZP_KEY_SECRET"))
                
                total = sum([bi.item_total for bi in basket_items]) * 100

                data = {"amount": total, "currency": "INR", "receipt": "order_rcptid_11"}
                
                payment = client.order.create(data=data)
                
                rzp_order_id = payment.get("id")
                
                order_instance.rzp_order_id = rzp_order_id
                
                order_instance.save()
                
                context = {
                    "amount": total,
                    "key_id":"shjbdbdkj",
                    "order_id": rzp_order_id,
                    "currency": "INR"
                }
                
                return render(request, "payment.html", context)
        
        return redirect('store:productlist')               
        
class OrderSummaryView(View):
    
    template_name = "order_summary.html"
    
    def get(self, request, *args, **kwargs):
        
        qs = reversed(request.user.orders.all())
        
        return render(request, self.template_name, {"orders": qs})   

@method_decorator(csrf_exempt, name="dispatch") 
class PaymentVerificationView(View):
    
    def post(self, request, *args, **kwargs):
        
        client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(request.POST)
            print("payment success")
            
            order_id = request.POST.get("razorpay_order_id")
            
            order_object = Order.objects.get(rzp_order_id=order_id)
            
            order_object.is_paid = True
            
            order_object.save()
            
            login(request, order_object.customer)
        except:
            print("payment-failed")
        
        return redirect('order-summary')
    
    from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Test view is working!")