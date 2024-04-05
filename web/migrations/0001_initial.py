# Generated by Django 4.2.11 on 2024-04-05 12:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.IntegerField(primary_key=True, serialize=False)),
                ("title", models.CharField()),
                ("description", models.CharField()),
                ("short_description", models.CharField()),
                ("genre", models.CharField()),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "stars",
                    models.IntegerField(
                        choices=[
                            (1, "Terrible"),
                            (2, "Poor"),
                            (3, "Average"),
                            (4, "Good"),
                            (5, "Excellent"),
                        ]
                    ),
                ),
                ("review", models.CharField()),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.CharField(max_length=25, primary_key=True, serialize=False),
                ),
                ("title", models.CharField(max_length=200)),
                ("release_date", models.DateField()),
                ("director", models.CharField(max_length=100)),
                ("runtime", models.IntegerField()),
                ("imdb_rating", models.FloatField()),
                ("description", models.TextField()),
                ("short_description", models.TextField()),
                ("genres", models.ManyToManyField(to="web.genre")),
                ("user_ratings", models.ManyToManyField(to="web.rating")),
            ],
        ),
    ]
