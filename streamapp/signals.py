from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from .models import settings_model

@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
            settings = settings_model(user=instance)
            settings.save()

            # Create directory for the user's files
            user_folder = f'media/att_data/{instance.username}'
            os.makedirs(user_folder, exist_ok=True)

            user_students = f'media/encode_images/{instance.username}'
            os.makedirs(user_students, exist_ok=True)

            user_students = f'Encodings/{instance.username}'
            os.makedirs(user_students, exist_ok=True)
