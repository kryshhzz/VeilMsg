# Generated by Django 4.1.5 on 2023-02-19 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0004_profile_veil_alter_profile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(default='Unleash your thoughts, connect anonymously, and go beyond appearances on veil 🕶️'),
        ),
    ]