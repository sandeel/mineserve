from django.contrib import admin
from .models import Server

class ServerAdmin(admin.ModelAdmin):
    exclude = ('id',)

admin.site.register(Server,ServerAdmin)
