from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import settings_model

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
            settings = settings_model(user=instance)
            settings.save()
