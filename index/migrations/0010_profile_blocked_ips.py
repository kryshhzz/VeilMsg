# Generated by Django 4.1.5 on 2023-03-27 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0009_ip_banned'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='blocked_ips',
            field=models.ManyToManyField(to='index.ip'),
        ),
    ]
