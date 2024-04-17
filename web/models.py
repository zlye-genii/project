from django.db import models
from user.models import Profile
from polymorphic.models import PolymorphicModel

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

class Person(models.Model):
    def __str__(self):
        return self.name
    name = models.CharField(max_length=100)
    url = models.URLField(null=True)

# are you here because of a "non nullable field" error?
# step 1: delete database
# step 2: delete all migration folders, keep __init__.py
# step 3: run dmigrate
# step 4: yippee!

class Media(PolymorphicModel):
    id = models.CharField(max_length=25, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True)
    release_date = models.DateField(null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    thumbnail = models.URLField(default='/static/banner404.png', null=True)

    def __str__(self):
        return self.title

class Movie(Media):
    directors = models.ManyToManyField(Person, blank=True)
    runtime = models.IntegerField(null=True) # mins
    imdb_rating = models.FloatField(null=True)
    content_rating = models.CharField(max_length=20, null=True)

class Book(Media):
    authors = models.ManyToManyField(Person, blank=True)
    pages = models.IntegerField()

class Rating(models.Model):
    stars = models.IntegerField(choices=StarRating.choices, default=StarRating.ZERO)
    review = models.TextField(null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='ratings')
    favorited = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.media.title}: {self.stars}{', ★' if self.favorited else ''}{', ✔' if self.completed else ''}" # star is NOT rating amount!!!! it is if favorited yes/no
