# Generated by Django 5.0.1 on 2024-01-31 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('liga', '0011_tournamentresult_deck'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='image',
            field=models.ImageField(default='default_deck_image.jpg', upload_to='deck_images/'),
        ),
    ]