# Generated by Django 4.1.7 on 2023-04-07 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0017_dm_viewonce'),
    ]

    operations = [
        migrations.AddField(
            model_name='dm',
            name='img',
            field=models.TextField(null=True),
        ),
    ]