from django.db import models
from user.models import Profile
from polymorphic.models import PolymorphicModel

# Create your models here.

class Genre(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100, unique=True)
    translated_name = models.CharField(max_length=100, unique=True, null=True)

class StarRating(models.IntegerChoices):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10

class Person(models.Model):
    def __str__(self):
        return self.name
    name = models.TextField()
    url = models.URLField(null=True)
class Media(PolymorphicModel):
    id = models.TextField(primary_key=True)
    title = models.TextField(null=True)
    description = models.TextField(null=True, max_length=10000)
    release_date = models.DateField(null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    thumbnail = models.TextField(default='/static/banner404.png', max_length=10000) # :<

    def __str__(self):
        return self.title

class Movie(Media):
    directors = models.ManyToManyField(Person, blank=True)
    runtime = models.IntegerField(null=True) # mins
    imdb_rating = models.FloatField(null=True)
    content_rating = models.TextField(null=True)

class Book(Media):
    authors = models.ManyToManyField(Person, blank=True)
    service_rating = models.FloatField(null=True)
    pages = models.IntegerField(null=True)

class Rating(models.Model):
    stars = models.IntegerField(choices=StarRating.choices, default=StarRating.ZERO)
    review = models.TextField(null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='ratings')
    favorited = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.media.title}: {self.stars}{', ★' if self.favorited else ''}{', ✔' if self.completed else ''}"
