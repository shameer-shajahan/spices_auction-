from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store'  

urlpatterns=[
    
    path('productlist/',views.SpiceListView.as_view(),name="productlist"),
    path('product/<int:pk>/',views.SpiceDetailView.as_view(),name="product-detail"),
    path('addtocart/<int:pk>/',views.AddtoCartView.as_view(),name="add-to-cart"),
    path('cart-summary',views.CartSummaryView.as_view(),name="cart-summary"),
    path('delete/<int:pk>',views.DeleteCartItemView.as_view(),name="delete"),
    path('place-order/',views.PlaceHolderView.as_view(),name="place-order"),
    path('order-summary/',views.OrderSummaryView.as_view(),name="order-summary"),
    path('payment/verify/',views.PaymentVerificationView.as_view(),name="payment-verify"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 
