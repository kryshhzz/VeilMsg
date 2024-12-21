"""dm_me URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from index.views import *
from blog.views import *
from verify.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",landing_view,name="landingView"),
    path("privacy-policy/",privacy_policy_view,name="privacyPolicyView"),
    path("blog/<slug:slug>",blog_view,name="blogView"),
    path("blog/",blogs_view,name="blogsView"),
    path("home/",index_view,name="indexView"),
    path("guest/",guest_view,name="guestView"),
    path("login/",login_view,name="loginView"),
    path("logout/",logout_view,name="logoutView"),
    path("signup/",signup_view,name="signupView"),
    path('pwd_reset/',pwd_reset_view, name='pwdReset'),
    path("inbox/",inbox_view,name="inboxView"),
    path("inbox/<int:pk>",dm_view,name="dmView"), 
    path("queries/",queries_view,name="queriesView"),
    path("block/<int:pk>", block_view,name="blockView"),
    path("edit-reply/<int:pk>",edit_reply_view,name="editReplyView"),
    path("user/",user_profile_view,name="userProfileView"),
    path("edit-profile/",edit_profile_view,name="editProfileView"),
    path("settings/",settings_view,name="settingsView"),
    path("user/<str:username>/",profile_view,name="profileView"),

]+ static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
