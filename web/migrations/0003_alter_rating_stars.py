# Generated by Django 4.2.11 on 2024-05-17 21:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0002_alter_media_thumbnail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rating",
            name="stars",
            field=models.IntegerField(
                choices=[
                    (0, "Zero"),
                    (1, "One"),
                    (2, "Two"),
                    (3, "Three"),
                    (4, "Four"),
                    (5, "Five"),
                    (6, "Six"),
                    (7, "Seven"),
                    (8, "Eight"),
                    (9, "Nine"),
                    (10, "Ten"),
                ],
                default=0,
            ),
        ),
    ]