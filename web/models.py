from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

# addon for djangos user
# includes a list of Ratings stuff and user data
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Genre(models.Model):
    name = models.CharField(max_length=100)

class StarRating(models.IntegerChoices):
    ONE = 1, 'Terrible'
    TWO = 2, 'Poor'
    THREE = 3, 'Average'
    FOUR = 4, 'Good'
    FIVE = 5, 'Excellent'

class Rating(models.Model):
    stars = models.IntegerField(choices=StarRating.choices)
    review = models.CharField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) 
    object_id = models.PositiveIntegerField()
    # genericforeignkey(content type, foreign key (unique movie/book object id))
    content_object = GenericForeignKey('content_type', 'object_id') # set/get media object here (movie, book)

# movie datal
# pull all this stuff from imdb scraper (not paying for an api key >_<)
# https://discord.com/channels/465439647334400001/1150680390902743060/1220148782000246944
class Movie(models.Model):
    id = models.CharField(max_length=25, primary_key=True)
    title = models.CharField(max_length=200)
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre)
    director = models.CharField(max_length=100)
    runtime = models.IntegerField() # mins
    imdb_rating = models.FloatField()
    user_ratings = models.ManyToManyField(Rating)
    description = models.TextField()
    short_description = models.TextField() # generate this once with ai and save it (yay, money saved!)
    # hack because no cascade delete on genericforeignkeys
    def delete(self, *args,**kwargs):
        Rating.objects.filter(content_type=ContentType.objects.get_for_model(self.__class__), object_id=self.id).delete()
        super().delete(*args, **kwargs)

class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField()
    description = models.CharField()
    short_description = models.CharField()
    genre = models.CharField()
    def delete(self, *args,**kwargs):
        Rating.objects.filter(content_type=ContentType.objects.get_for_model(self.__class__), object_id=self.id).delete()
        super().delete(*args, **kwargs)
