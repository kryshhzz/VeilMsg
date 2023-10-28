from django.db import models

# Create your models here.

class blog(models.Model):
    title  =  models.TextField()
    link = models.TextField()
    slug = models.SlugField()
    createdAt = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title