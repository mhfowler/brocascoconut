from django.http import HttpResponse
from django import shortcuts
from mhf.models import Stat


def redirect(request, page='/home'):
    return shortcuts.redirect(page)


def viewWrapper(view):
    def new_view(request, *args, **kwargs):
        return view(request,*args,**kwargs)
    return new_view


def home(request):
    stats = Stat.objects.all()
    return HttpResponse("Miley do what she want doe yup")
    # return shortcuts.redirect("/blog/")