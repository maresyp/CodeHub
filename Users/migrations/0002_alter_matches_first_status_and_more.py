# Generated by Django 4.0 on 2023-07-03 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matches',
            name='first_status',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matches',
            name='second_status',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
