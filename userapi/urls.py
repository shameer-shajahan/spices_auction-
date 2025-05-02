from django.urls import path
from userapi import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/',views.RegView.as_view(),name="signup"),
    path('signin/',views.SignInView.as_view(),name="signin"),
    path('logout/',views.logoutuser,name="logout"),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path("auctions/",views.AuctionsListView.as_view(),name="auctions-list"),
    path("bid/",views.bids_list_view,name="bid-list"),
    path("products/",views.ProductsListView.as_view(),name="products-list"),
    path('delete-bid/<int:bid_id>/', views.delete_bid_view, name='delete_bid'),
    path("products/add/",views.ProductsAddView.as_view(),name="products-add"),
    path("products/<int:pk>/remove/",views.remove_product,name="products-remove"),
    path("products/<int:pk>/add/",views.AuctionAddView.as_view(),name="auction-add"),
    path('place-bid/<int:pk>/', views.place_bid.as_view(), name='place_bid'),
    path("wonbids/",views.wonbids_view,name="wonbids"),
    path("makepayment/",views.create_payment,name="payment"),
    path('download-bill/<int:bid_id>/', views.download_bill, name='download_bill'),
    path('download-slip/<int:bid_id>/', views.download_slip, name='download_slip'),
    path("feedback/",views.AddfeedbackView.as_view(),name="feedback-add"),
    path('card_input/<int:bid_id>/', views.card_input, name='card_input'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('', views.landingpage, name='index'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),

    





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
