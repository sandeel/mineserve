from django.shortcuts import render
from .models import Server
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from users.forms import SalePaymentForm


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

def topup(request, server_id):
    if request.method == "POST":
        form = SalePaymentForm(request.POST, user=request.user, server_id=server_id)

        if form.is_valid(): # charges the card
            return HttpResponse("Success! We've charged your card!")
    else:
        form = SalePaymentForm()

    return render(request, "servers/topup.html", {'form': form} )
