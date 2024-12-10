# liga/admin.py

from django.contrib import admin
from .models import Player, TournamentType,TournamentResult, Tournament, Deck, Ranking

admin.site.register(Player)
admin.site.register(TournamentType)
admin.site.register(TournamentResult)
admin.site.register(Tournament)
admin.site.register(Deck)
admin.site.register(Ranking)