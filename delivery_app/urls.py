from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "delivery_app"

urlpatterns = [
    path('home/', views.home, name='delivery_home'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('assigned/orders/', views.AssignedOrdersView.as_view(), name='assigned_orders'),
    path('order/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('completed-orders/', views.CompletedOrdersView.as_view(), name='completed_orders'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
