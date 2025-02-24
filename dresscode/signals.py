from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Sukuria naują profilį, kai sukuriamas naujas vartotojas."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Išsaugo vartotojo profilį, kai vartotojo informacija atnaujinama."""
    instance.profile.save()
