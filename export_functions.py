import sys
import os

# Adiciona o diretório liga ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'liga'))

from liga.firebase_config import db
from liga.models import Player, Tournament, TournamentResult, Deck, Ranking

# Função para exportar jogadores para o Firestore
def export_players_to_firestore():
    players = Player.objects.all()
    for player in players:
        doc_ref = db.collection('players').document(str(player.official_id))
        doc_ref.set({
            'name': player.name,
            'official_id': player.official_id,
            'contact': player.contact,
            'weekly_wins': TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='Semanal').count(),
            'premiere_wins': TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='Premiere').count(),
            'ots_wins': TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='OTS').count()
        })

# Função para exportar torneios para o Firestore
def export_tournaments_to_firestore():
    tournaments = Tournament.objects.all()
    for tournament in tournaments:
        doc_ref = db.collection('tournaments').document(str(tournament.id))
        doc_ref.set({
            'name': tournament.name,
            'date': tournament.date.isoformat(),
            'tournament_type': tournament.tournament_type.name,
            'results': [
                {
                    'player_id': result.player.official_id,
                    'position': result.position,
                    'points': result.points,
                    'deck': result.deck.name
                }
                for result in TournamentResult.objects.filter(tournament=tournament)
            ]
        })

# Função para exportar decks para o Firestore
def export_decks_to_firestore():
    decks = Deck.objects.all()
    for deck in decks:
        doc_ref = db.collection('decks').document(str(deck.id))
        doc_ref.set({
            'name': deck.name
            
        })

# Função para exportar rankings para o Firestore
def export_rankings_to_firestore():
    rankings = Ranking.objects.all()
    for ranking in rankings:
        doc_ref = db.collection('rankings').document(str(ranking.id))
        doc_ref.set({
            'player_id': ranking.player.official_id,
            'total_points': ranking.total_points  # Certifique-se de usar o campo correto
        })
