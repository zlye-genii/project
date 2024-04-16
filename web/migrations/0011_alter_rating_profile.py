# Generated by Django 4.2.11 on 2024-04-16 11:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_profile_ratings"),
        ("web", "0010_rating_profile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rating",
            name="profile",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="user.profile",
            ),
        ),
    ]
