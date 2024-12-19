from django.shortcuts import render
from .models import *
# Create your views here.

def blog_view(request,slug):
    ex_blog = blog.objects.filter(slug=slug)
    if len(ex_blog) > 0:
        cont = {
            'blog' : ex_blog[0],
        }
        return render(request,'blog/'+ex_blog[0].link,cont)

def blogs_view(request):
    ex_blog = blog.objects.all()
    cont = {
        'blogs' : ex_blog,
    }
    return render(request,'blog/index.html',cont)
