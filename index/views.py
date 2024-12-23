from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from datetime import timedelta, datetime,timezone
import traceback,base64, random
from django.db.models.functions import Now
from .models import *
from .forms import *
from verify.views import deleteOldGuests
from .mail import *
from .Dum import *

from django.core.files.base import ContentFile
# Create your views here


def checkMessages(user,cont):
  dms = dm.objects.filter(sentTo=user,opened=False).order_by("-pk")
  unseenmsgs = False
  if len(dms) > 0:
    unseenmsgs = True
    cont |= {
        "unseenMsgs" : unseenmsgs,
    }
  #deljunk()
  return cont

def checkQueries(user,cont):
  dms2 = dm.objects.filter(sentBy__owner=user,isQuery=True,opened=True).order_by("-pk")
  unseenQResps = False
  if len(dms2) > 0:
    unseenQResps = True
    cont |= {
        "unseenQResps" : unseenQResps,
    }
  #deljunk()
  return cont

def deleteOldData():
  dfx = Now() - timedelta(days=1)
  deldms = dm.objects.filter(opened = True,sentAt__lte = dfx,isQuery=False)
  deldms |= dm.objects.filter(opened=True, viewOnce=True,isQuery=False)
  #removing pinned dms from deleteable dms
  pinned_replies = reply.objects.filter(pinned=True)
  for pinned_reply in pinned_replies :
    deldms = deldms.exclude(pk=pinned_reply.replyTo.pk)
  deldms.delete()
  #deleting old queries
  dfx = Now() - timedelta(days=7)
  deldms = dm.objects.filter(opened = True,sentAt__lte = dfx,isQuery=True)
  deldms.delete()



def congratulate(msg,usr):
    ip_admin = IP.objects.filter(id=86)
    x = dm.objects.create(message=msg,sentTo=usr,sentBy=ip_admin[0],isNotif=True,viewOnce=False)
    x.save()

def checkLevel(usr):
    msg1 = "Congratulations "+usr.first_name+" on earning 10 veil points. You are officially a Veil-Spark from now ✨ Keep Engaging !"
    msg2 = "Congratulations "+usr.first_name+" on earning 100 veil points. You are officially a Veil-Rocket from now.️ Keep Blazing !"
    msg3 = "Congratulations "+usr.first_name+" on earning 500 veil points. You are officialy a Veil-Comet from now ☄ Keep Captivating !"
    msg4 = "Congratulations "+usr.first_name+" on earning 1000 veil points. You are officialy a Veil-SuperNova from now ☄ Keep Captivating !"

    if usr.profile.dms_count == 10 :
        congratulate(msg1,usr)
    elif usr.profile.dms_count == 100 :
        congratulate(msg2,usr)
    elif usr.profile.dms_count == 500 :
        congratulate(msg3,usr)
    elif usr.profile.dms_count == 1000 :
        congratulate(msg4,usr)


def return_replies(usr,cont):
    replies = reply.objects.filter(replyTo__sentTo=usr,replyTo__isQuery=False).order_by('-pinned',"-pk")
    cont["replies"] = replies

def return_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get("REMOTE_ADDR")
  return ip

def profile_view(request,username):
  usr = User.objects.filter(username=username)
  if len(usr) == 0 :
      return  HttpResponseNotFound("<h1>Account not found bro/sis 😔</h1>")
  cont = {}
  cont |= {
    "user" : usr[0],
    "title" : "'"+usr[0].first_name+"' : "+usr[0].profile.bio,
  }
  try:
    cont["userdp"] = "/"+"/".join(usr[0].profile.dp.url.split("/")[2:])
  except :
    pass

  cont |= checkMessages(usr[0],cont)
  cont |= checkQueries(usr[0],cont)
  if len(usr) > 0 :
    return_replies(usr[0],cont)
    if request.method == "POST":
      msgType = request.POST.get('msgType')
      vibe = request.POST.get('vibe')
      msg = request.POST.get("message")
      img = request.POST.get('msgImg')
      viewonce = request.POST.get('viewonce')
      viewOnce = False
      if viewonce == 'on' :
        viewOnce = True
      try :
        ip = return_ip(request)
        ip_final = IP.objects.none() #final ip

        ip_list = IP.objects.filter(address=ip)
        if len(ip_list) > 0 :
          ip_final = ip_list[0]
        else :
          z = IP.objects.create(address=ip)
          z.save()
          ip_final = z

        if request.user.is_authenticated == True and ip_final.owner is None:
          ip_final.owner = request.user
          ip_final.save()

        if ip_final.banned == True :
            cont["status"] =  "You are temporarily banned from sending messages !"
            return render(request,"profile.html",cont)

        if not usr[0].profile.blocked_ips.filter(pk=ip_final.pk).exists() and usr[0].profile.is_open  :
          isnotif = False
          isQuery = False
          if request.user.username == "admin" :
              isnotif = True
          if usr[0].username == 'admin' :
              isQuery = True
          x = dm.objects.create(sentTo=usr[0], sentBy = ip_final, viewOnce = viewOnce, isNotif = isnotif, isQuery=isQuery, dmType=msgType)
          if msgType == '1' :
            x.message=msg
          elif msgType == '2' :
            if img is not None and len(img) > 24 and img[:len('data:image/jpeg;base64')] == 'data:image/jpeg;base64' :
                x.img = img
          elif msgType == '3':
            x.message = vibe
          x.save()
          usr[0].profile.dms_count += 1
          usr[0].save()
          checkLevel(usr[0])
          #cont["status"] = "Message sent successfully !"
          send_mail(usr[0].pk)
          return redirect('/user/'+usr[0].username+'/?status=S')
        else :
          #cont["status"] = "You cannot send dms to @"+usr[0].username+" !"
          return redirect('/user/'+usr[0].username+'/?status=B')
      except Exception as e :
        print(traceback.format_exc())
        #cont["status"] = "Some error occurred !"
        return redirect('/user/'+usr[0].username+'/?status=E')
  return render(request,"profile.html",cont)


def user_profile_view(request):
  if request.user.is_authenticated == False:
    return redirect("/login/")
  usr = request.user

  cont = {
    "usr" : usr,
    "user_profile" : True,
  }
  try:
    cont["userdp"] = "/"+"/".join(usr.profile.dp.url.split("/")[2:])
  except:
    pass
  return_replies(usr,cont)
  cont = checkMessages(usr,cont)
  cont = checkQueries(usr,cont)
  return render(request,"profile.html",cont)

def edit_profile_view(request):
  if request.user.is_authenticated == False:
    return redirect("/login/")
  usr = request.user
  dict = {
      "user":usr,
      'emojis' : emojis.objects.all(),
      }
  try :
      dict["userdp"] = "/"+"/".join(usr.profile.dp.url.split("/")[2:])
  except :
      pass
  if request.method == "POST":
    if request.POST.get("veil").strip() != "" :
        image_data = request.POST.get("veil").strip()
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr))
        file_name = usr.username+"_" + str(random.randint(100, 999999))+"."+ ext
        usr.profile.dp.delete()
        usr.profile.dp.save(file_name, data, save=True)

    # username = request.POST.get("username").strip()
    # if User.objects.filter(username=username).exists() :
    #     if not usr.username == username :
    #         dict["error"] =   "Choose a different username"
    #         return render(request,"edit_profile.html",dict)

    # if any(c in "@#£&-+()/*':;!?.,~`|•√π÷×§∆€¥$¢^°={}\%©®™✓[]\"" for c in username) :
    #     dict["error"] =  "Choose another username"
    #     return render(request,"edit_profile.html",dict)

    # usr.username = username
    usr.first_name = request.POST.get("name").strip()
    usr.profile.bio = request.POST.get("bio").strip()
    usr.profile.bg_color = request.POST.get("profile_bg").strip()
    usr.save()
    return redirect("/user/")

  return render(request,"edit_profile.html",dict)

def settings_view(request):
  if request.user.is_authenticated == False:
    return redirect("/login/")

  existing_profile = profile.objects.filter(user=request.user)[0]
  cont = {}
  if request.method == 'POST':
    form = SettingsForm(request.POST, instance=existing_profile)
    if form.is_valid():
        x = form.save(commit=False)
        x.save()
        cont['status'] = 'Open status changed !'

  cont |= {
    "user": request.user,
    "form" : SettingsForm(instance=existing_profile),
  }
  return render(request,"settings.html",cont)

def inbox_view(request):
  if request.user.is_authenticated == False:
    return redirect("/login/")
  dms = dm.objects.filter(sentTo=request.user).order_by("-pk")
  #######
  deleteOldData()
  #######
  cont = {"dms":dms}
  cont = checkQueries(request.user,cont)
  return render(request,"inbox.html",cont)

def queries_view(request):
    if request.user.is_authenticated == False:
        return redirect("/login/")
    dms2 = [] 
    dms = dm.objects.filter(sentBy__owner=request.user,isQuery=True).order_by("-pk") 

    for dmeach in dms :
        reps = reply.objects.filter(replyTo=dmeach)
        if len(reps) > 0:
            temp = {
                'dm' : dmeach,
                'reply' : reps[0].reply,
            }
        else :
            temp = {
                'dm' : dmeach,
                'reply' : '',
            }
        dms2.append(temp)
    cont = {"dms_list":dms2}
    cont = checkMessages(request.user,cont) 
    return render(request,"queries.html",cont)

def dm_view(request,pk):
  if request.user.is_authenticated == False:
    return redirect("/login/")
  dms = dm.objects.filter(pk=pk,sentTo=request.user)
  if len(dms) > 0 :
    dms[0].opened=True
    dms[0].save()

    cont = {
      "dm":dms[0],
      "user" : request.user,
    }
    try :
        cont["userdp"] = "/"+"/".join(request.user.profile.dp.url.split("/")[2:])
    except:
        pass
    # replies
    if request.method == "POST":
        replyText = request.POST.get("dm-reply")
        rep = reply.objects.create(reply=replyText,replyTo=dms[0])
        rep.save()
        cont["status"] = "replied succesfully !"
    return render(request,"dm.html",cont)
  else :
    return HttpResponseNotFound("page not found")

def block_view(request, pk):
  if request.user.is_authenticated == False:
    return redirect("/login/")

  final_ip = IP.objects.filter(pk=pk)
  if len(final_ip) > 0 :
    cont = {
      "user": request.user,
      "dms" : dm.objects.filter(sentTo=request.user).order_by("-pk"),
    }
    if request.GET.get("unblock") == "true":
      request.user.profile.blocked_ips.remove(final_ip[0])
      cont["status"] = "Unblocked this user !"
      return render(request,"settings.html",cont)
    else :
      request.user.profile.blocked_ips.add(final_ip[0])
      cont["status"] = "Blocked this user !"
      return render(request,"inbox.html",cont)

def edit_reply_view(request,pk):
  if request.user.is_authenticated == False:
    return redirect("/login/")

  pin = request.GET.get("pin")
  delete = request.GET.get("delete")

  rep = reply.objects.filter(pk=pk)
  if len(rep) > 0 and rep[0].replyTo.sentTo == request.user :
    if pin == "true" :
      if rep[0].pinned == True :
        rep[0].pinned = False
        rep[0].save()
      else :
        rep[0].pinned = True
        rep[0].save()
    elif delete == "true" :
      rep[0].delete()

  return redirect("/user/")

def index_view(request):
  #########
  deleteOldGuests()
  #########
  if request.user.is_authenticated == False:
    return redirect("/login/")

  time_ahead = request.user.date_joined + timedelta(hours=48)
  time_difference = time_ahead - datetime.now(timezone.utc)
  hours, remainder = divmod(int(time_difference.total_seconds()), 3600)
  minutes, seconds = divmod(remainder, 60)
  formatted_duration = f"{hours:02d}hrs {minutes:02d}mins"
  print(formatted_duration)

  cont = {
    "user" : request.user,
    'time_diff' : formatted_duration,
  }
  cont = checkMessages(request.user,cont)
  cont = checkQueries(request.user,cont)
  return render(request,"index.html",cont)

def landing_view(request):
    if request.user.is_authenticated == True :
        return redirect('/home')
    return render(request,"landing.html",{})
    #return redirect('/home/')

def privacy_policy_view(request):
    return render(request,'privacy-policy.html',{})