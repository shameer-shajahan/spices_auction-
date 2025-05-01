from django.contrib import admin
from store.models import Order,OrderItem,Category,Spice,Origin,ProcessingType,Quality,Basket,BasketItem

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(    Spice)
admin.site.register(Origin)
admin.site.register(ProcessingType)
admin.site.register(Quality)
