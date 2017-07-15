from django.shortcuts import render
from .models import Server


def index(request):
    server_list = Server.objects.all()
    context = {'server_list': server_list}
    return render(request, 'servers/index.html', context)
