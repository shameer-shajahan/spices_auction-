from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from random import randint
from adminapi.models import CustomUser
   
       
class BaseModel(models.Model):
    created_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)

class Origin(BaseModel):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name

class ProcessingType(BaseModel):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name
   
class Category(BaseModel):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name
   
class Quality(BaseModel):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Spice(BaseModel):
    title=models.CharField(max_length=200)
    description=models.TextField()
    price=models.PositiveIntegerField()
    picture=models.ImageField(upload_to="spice_images",null=True,blank=True)
    origin_object=models.ForeignKey(Origin,on_delete=models.CASCADE)
    category_object=models.ForeignKey(Category,on_delete=models.CASCADE)
    quality_objects=models.ManyToManyField(Quality)
    stock_quantity=models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.title

class Basket(BaseModel):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE,related_name="cart")

class BasketItem(BaseModel):
    spice_object=models.ForeignKey(Spice,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    is_order_placed=models.BooleanField(default=False)
    basket_object=models.ForeignKey(Basket,on_delete=models.CASCADE,related_name="cart_item")
   
    @property
    def item_total(self):
        return self.spice_object.price*self.quantity

# Function to create basket when user is created
def create_basket(sender,instance,created,**kwargs):
    if created:
        Basket.objects.create(user=instance)
       
post_save.connect(create_basket,CustomUser)
   
class Order(BaseModel):
    customer=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="orders")
    address=models.TextField()
    phone=models.CharField(max_length=20)
    PAYMENT_OPTIONS=(
        ("COD","COD"),
        ("ONLINE","ONLINE")
    )
    payment_method=models.CharField(max_length=15,choices=PAYMENT_OPTIONS,default="COD")
    rzp_order_id=models.CharField(max_length=100,null=True)
    is_paid=models.BooleanField(default=False)
   
    @property
    def order_total(self):
        total=sum([oi.item_total for oi in self.orderitems.all()])
        return total

class OrderItem(BaseModel):
    order_object=models.ForeignKey(
                                   Order,on_delete=models.CASCADE,
                                   related_name="orderitems"
                                   )
   
    spice_object=models.ForeignKey(Spice,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.FloatField()
   
    @property
    def item_total(self):
        return self.price*self.quantity