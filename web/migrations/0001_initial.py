# Generated by Django 4.2.11 on 2024-04-18 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('title', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('release_date', models.DateField(null=True)),
                ('thumbnail', models.URLField(default='/static/banner404.png', null=True)),
                ('genres', models.ManyToManyField(blank=True, to='web.genre')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.IntegerField(choices=[(0, 'None'), (1, 'Terrible'), (2, 'Poor'), (3, 'Average'), (4, 'Good'), (5, 'Excellent')], default=0)),
                ('review', models.TextField(blank=True, null=True)),
                ('favorited', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='web.media')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='user.profile')),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('media_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web.media')),
                ('runtime', models.IntegerField(null=True)),
                ('imdb_rating', models.FloatField(null=True)),
                ('content_rating', models.CharField(max_length=20, null=True)),
                ('directors', models.ManyToManyField(blank=True, to='web.person')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('web.media',),
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('media_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='web.media')),
                ('pages', models.IntegerField()),
                ('authors', models.ManyToManyField(blank=True, to='web.person')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('web.media',),
        ),
    ]
