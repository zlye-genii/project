from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up

# Create your models here.

# addon for djangos user
# includes a list of Ratings stuff and user data
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

@receiver(user_signed_up)
def create_profile(sender, **kwargs):
    user = kwargs['user']
    Profile.objects.create(user=user)