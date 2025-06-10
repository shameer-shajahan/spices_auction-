from django.urls import path
from adminapi import views



urlpatterns=[
    
    path("login/",views.SignInView.as_view(),name="adminsignin"),
    path("logout/",views.signoutview,name="adminsignout"),
    path("home/",views.HomeView.as_view(),name="home"),
    path("bids/",views.BidsView.as_view(),name="bids"),
    path('bid/delete/<int:pk>/',views.BidDeleteView.as_view(), name='bid_delete'),
    path("products/",views.ProductsView.as_view(),name="products"),
    path('product/delete/<int:pk>/',views.SpiceDeleteView.as_view(), name='spice_delete'),
    path("sellers/",views.CustomerView.as_view(),name="sellers"),
    path("feedbacks/",views.FeedbacksView.as_view(),name="feedbacks"),
    path("auctions/",views.AuctionsView.as_view(),name="auctions"),
    path('auction/delete/<int:pk>/',views.AuctionDeleteView.as_view(), name='auction_delete'),
    path("payments/",views.PaymentsView.as_view(),name="payments"),
    path('seller/delete/<int:pk>/',views.SellerDeleteView.as_view(), name='seller_delete'),
    path('completed-payments/', views.CompletedPaymentsView.as_view(), name='completed_payments'),
    path('assign-agent/<int:purchase_id>/', views.assign_delivery_agent, name='assign_delivery_agent'),
    
# delivery urls

    path('create-agent/', views.create_delivery_agent, name='create_delivery_agent'),
    path('agents/', views.delivery_agent_list, name='delivery_agent_list'),
    path('agents/<int:pk>/edit/', views.edit_delivery_agent, name='edit_delivery_agent'),
    path('agents/<int:pk>/delete/', views.delete_delivery_agent, name='delete_delivery_agent'),

]