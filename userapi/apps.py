from django.apps import AppConfig
from django.db.models.signals import pre_save
from django.dispatch import receiver


class UserapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userapi'

        
