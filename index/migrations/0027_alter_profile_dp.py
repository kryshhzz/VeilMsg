# Generated by Django 4.0.6 on 2023-12-01 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0026_alter_profile_dp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='dp',
            field=models.ImageField(blank=True, default='', upload_to='static/profile_pics/'),
        ),
    ]