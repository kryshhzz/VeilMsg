from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(dm)
admin.site.register(profile)
admin.site.register(reply)
admin.site.register(IP)
admin.site.register(emojis)