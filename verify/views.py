from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.models import User
import random,base64
from datetime import timedelta
from django.db.models.functions import Now
from index.models import *
from django.core.files.base import ContentFile
# Create your views here.

def deleteOldGuests():
  dfx = Now() - timedelta(hours=48)
  delguests = profile.objects.filter(tier = 1,user__date_joined__lte = dfx)
  user_ids = delguests.values_list('user_id', flat=True)
  User.objects.filter(id__in=user_ids).delete()

def generate_username(name):
  name = name.strip()
  x = name.split(" ")
  y = x[0].lower()
  for let in "@#₹&-+()/*':;!?,.~`|•√π÷×¶∆€¥$¢^°={}\%©®™✓[]" :
    if let in y :
      y = y.replace(let,"")
  y = y.replace('"','')
  z = random.randrange(10000,999999,1)
  usr = y+"_"+str(z)
  if User.objects.filter(username=usr).exists() :
    generate_username(name)
  return usr

def set_default_dp(usr):
    emoji = random.choice(emojis.objects.all())
    image_data = emoji.data
    format, imgstr = image_data.split(';base64,')
    ext = format.split('/')[-1]
    data = ContentFile(base64.b64decode(imgstr))
    file_name = usr.username+"_" + str(random.randint(100, 999999))+"."+ ext
    usr.profile.dp.delete()
    usr.profile.dp.save(file_name, data, save=True)

def guest_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = generate_username('guest')
        password = random.randrange(10000,999999,1)

        user = User.objects.create_user(username=username, password=str(password), last_name=str(password), first_name=name)
        user.save()

        set_default_dp(user)

        usr = authenticate(username=username, password=password)
        if usr is not None :
            login(request,usr)
            return redirect("/home/")
        else :
            dict = {"error": "An error occured.. try to login again"}
    return render(request,"guest.html",{})

def login_view(request):
  if request.user.is_authenticated == True:
    return redirect("/home/")
  dict = {}
  if request.method == "POST":
    username = request.POST.get("username").strip()
    password = request.POST.get("password")

    if "@" in username :
      usrs = User.objects.filter(email=username)
      if len(usrs) > 0:
        username = usrs[0].username

    usr = authenticate(username=username, password=password)
    if usr is not None :
      login(request,usr)
      return redirect("/home/")
    else :
      dict = {"error": "Wrong username / email or password !"}
  return render(request,"login.html",dict)


def signup_view(request):
  # redirecting to homepage if logged in
  dict = {}
  if request.method == "POST":
    email = request.POST.get("email").strip()
    name = request.POST.get("name").strip()
    secque = request.POST.get("secque").strip()
    password = request.POST.get("password")

    unqemail = User.objects.filter(email=email)
    username = generate_username(name)

    if len(unqemail) > 0 :
      dict = {"error" : "email already in use"}
    else :
      user = User.objects.create_user(username=username,email=email, password=password, first_name=name)
      user.profile.tier = 2
      user.profile.secque = secque
      user.save()

      set_default_dp(user)

      usr = authenticate(username=username, password=password)
      if usr is not None :
        login(request,usr)
        return redirect("/home/")
      else :
        dict = {"error": "An error occured.. try to login again"}

  return render(request,"signup.html",dict)

def pwd_reset_view(request):
    if request.user.is_authenticated == True:
        return redirect("/home/")
    dict = {}
    if request.method == "POST":
        username = request.POST.get('username')
        secque = request.POST.get('secque')

        dict['username'] = username

        if "@" in username :
          usrs = User.objects.filter(email=username)
          if len(usrs) > 0:
            username = usrs[0].username

        usr = User.objects.filter(username=username)
        if len(usr) == 0:
            dict = {"error": "No such user exists !"}
        else :
            if usr[0].profile.secque == secque :
                login(request, usr[0]) 
                return redirect('/')
            else :
                dict = {"error": "wrong answer !"}

    return render(request,"pwd_reset.html",dict)


def logout_view(request):
  logout(request)
  return redirect("/login/")