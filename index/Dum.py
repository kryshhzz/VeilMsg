from .models import *

def deljunk():
    for ip in IP.objects.all():
        if not dm.objects.filter(sentBy = ip).exists():
            ip.delete()

