from django.shortcuts import render
from .models import Server
from django.views.generic.edit import CreateView


def index(request):
    server_list = Server.objects.filter(user=request.user)
    context = {'server_list': server_list}
    return render(request, 'servers/index.html', context)


class ServerCreate(CreateView):
    model = Server
    fields = [
        'server_type',
        'region',
    ]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        return super(ServerCreate, self).form_valid(form)
