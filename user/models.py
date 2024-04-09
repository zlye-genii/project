from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# addon for djangos user
# includes a list of Ratings stuff and user data
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)