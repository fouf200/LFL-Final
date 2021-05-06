from django.contrib import admin
from .models import Players, Team, Game, Event,Accounts
# Register your models here.

admin.site.register(Accounts)
admin.site.register(Players)
admin.site.register(Team)
admin.site.register(Game)
admin.site.register(Event)
