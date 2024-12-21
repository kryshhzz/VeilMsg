from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from datetime import timedelta
# Create your models here.

class emojis(models.Model):
  name = models.TextField(blank=False,null=False)
  data = models.TextField(blank=False,null=False)

  def __str__(self):
    return self.name

class IP(models.Model):
  address = models.GenericIPAddressField(unique=True)
  owner = models.ForeignKey(User, null=True,default= None, on_delete=models.SET_DEFAULT )
  banned = models.BooleanField(default=False)
  createdAt = models.DateTimeField(auto_now_add=True, null=True)

  def __str__(self):
    return self.address

#tier 1 = guests
#tier 2 = normal users
#tier 3 = pro users

class profile(models.Model):
  user = models.OneToOneField(User,on_delete=models.CASCADE)
  bio = models.TextField(default="Send anonymous messages to me !")
  dp = models.ImageField(default="", blank= True, upload_to="veil/static/profile_pics/")
  bg_color = models.CharField(default="", blank=True, null=True, max_length=7)
  dms_count = models.IntegerField(default=0)
  blocked_ips = models.ManyToManyField(IP,blank=True)
  is_open = models.BooleanField(default=True)
  tier = models.IntegerField(default=1, blank=False,null=False)
  secque = models.CharField(max_length=255, blank=True, default='')

  def __str__(this):
    return this.user.username +" - "+ this.user.first_name + " [ "+str(this.dms_count)+" ]"

@receiver(pre_delete, sender=profile)
def delete_profile_picture(sender, instance, **kwargs):
    instance.dp.delete()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created :
    profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()


class dm(models.Model):
  message = models.TextField(null=True)
  sentTo = models.ForeignKey(User, on_delete=models.CASCADE)
  sentAt = models.DateTimeField(auto_now_add=True)
  opened = models.BooleanField(default=False)
  sentBy = models.ForeignKey(IP, null=True, on_delete=models.SET_NULL)
  isNotif = models.BooleanField(default=False)
  isQuery = models.BooleanField(default=False)
  viewOnce = models.BooleanField(default=False, null = False, blank=False)
  dmType = models.IntegerField(null=False, blank=False, default=1)
  img = models.TextField(null=True,blank=True)

  def __str__(self):
    return self.sentTo.first_name+" [ "+(self.sentAt+ timedelta(hours=5,minutes=30)).strftime("%d/%m/%Y  %H:%M") +" ] :"+str(self.dmType)

@receiver(pre_delete,sender=dm)
def delete_ip(sender,instance,**kwargs):
    ip = instance.sentBy
    if ip.banned == False :
        if not profile.objects.filter(blocked_ips = ip).exists():
            if len( dm.objects.filter(sentBy = ip) ) <= 1 :
                ip.delete()


class reply(models.Model):
    reply = models.TextField()
    replyTo = models.ForeignKey(dm, on_delete = models.CASCADE)
    replyAt = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)

    def __str__(self):
        return self.replyTo.sentTo.username+" [ "+(self.replyAt+ timedelta(hours=5,minutes=30)).strftime("%d/%m/%Y  %H:%M") +" ]"


