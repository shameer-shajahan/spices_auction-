from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Basket

@receiver(post_save, sender=CustomUser)
def create_user_cart(sender, instance, created, **kwargs):
    """
    Create a cart for a user when they are created
    """
    if created:
        Basket.objects.create(user=instance)