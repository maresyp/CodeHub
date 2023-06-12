# Generated by Django 4.0 on 2023-06-12 19:03

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('Codes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('age', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(18), django.core.validators.MaxValueValidator(125)])),
                ('bio', models.TextField(blank=True, max_length=1000, null=True)),
                ('profile_image', models.ImageField(blank=True, default='profiles/user-default.png', null=True, upload_to='profiles')),
                ('gender', models.CharField(choices=[('M', 'Mężczyzna'), ('K', 'Kobieta')], default='M', max_length=1)),
                ('social_github', models.CharField(blank=True, max_length=2000, null=True)),
                ('social_twitter', models.CharField(blank=True, max_length=2000, null=True)),
                ('social_youtube', models.CharField(blank=True, max_length=2000, null=True)),
                ('social_linkedin', models.CharField(blank=True, max_length=2000, null=True)),
                ('social_facebook', models.CharField(blank=True, max_length=2000, null=True)),
                ('favourite_code', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Codes.code')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Matches',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('first_status', models.BooleanField()),
                ('second_status', models.BooleanField()),
                ('first_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='first_user', to='auth.user')),
                ('second_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='second_user', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='FavouritesTags',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('value', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('tag_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Codes.tag')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
