from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from user.models import Profile

# Create your models here.

class Genre(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100, unique=True)

class StarRating(models.IntegerChoices):
    ZERO = 0, 'None' # kind of a hack to allow favorited without a rating :p
    ONE = 1, 'Terrible'
    TWO = 2, 'Poor'
    THREE = 3, 'Average'
    FOUR = 4, 'Good'
    FIVE = 5, 'Excellent'

class Director(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100)
    url = models.URLField()

# TODO: merge these two into one Media object with foreignkey contenttype
class Movie(models.Model):
    def __str__(self):
        return self.title
    id = models.CharField(max_length=25, primary_key=True)
    title = models.CharField(max_length=200)
    release_date = models.DateField(null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    directors = models.ManyToManyField(Director, blank=True)
    runtime = models.IntegerField(null=True) # mins
    imdb_rating = models.FloatField(null=True)
    description = models.TextField(null=True)
    poster_url = models.URLField(default='/static/banner404.png', null=True)
    content_rating = models.CharField(max_length=20, null=True)
    def delete(self, *args,**kwargs):
        self.ratings.all().delete()
        super().delete(*args, **kwargs)

class Rating(models.Model):
    def __str__(self):
        return f"{self.media.title}: {self.stars}{', ★' if self.favorited else ''}" # star is NOT rating amount!!!! it is if favorited yes/no
    stars = models.IntegerField(choices=StarRating.choices, default=StarRating.ZERO)
    review = models.TextField(null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)
    media = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings', default=None) # why do you want a default, none of you should be null anyway??
    favorited = models.BooleanField(default=False)

class Book(models.Model):
    def __str__(self):
        return self.title
    id = models.IntegerField(primary_key=True)
    title = models.CharField()
    description = models.CharField()
    short_description = models.CharField()
    genre = models.CharField()
    def delete(self, *args,**kwargs):
        self.ratings.all().delete()
        super().delete(*args, **kwargs)
