# Generated by Django 4.0 on 2023-06-30 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Codes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='file_extension',
            field=models.CharField(default='js', max_length=10, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='codetags',
            name='code_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Codes.code'),
        ),
    ]
