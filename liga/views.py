# liga/views.py

from django.shortcuts import render, redirect  # Não se esqueça de importar redirect
from .forms import PlayerRegistrationForm
from django.contrib import messages
from .models import Tournament, Ranking, TournamentResult, Deck, Player
from .forms import PlayerRegistrationForm, TournamentRegistrationForm, TournamentResultForm, DeckRegistrationForm
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404
import csv
from django.http import HttpResponse
from django.db.models import Count
from django.db import models

def home(request):
    return render(request, 'home.html')

def tournament_day(request):
    # Obter todos os torneios
    tournaments = Tournament.objects.all()
    # Passar os torneios para o template
    return render(request, 'tournament_day.html', {'tournaments': tournaments})

def player_registration(request):
    if request.method == 'POST':
        form = PlayerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Jogador cadastrado com sucesso!')
            return redirect('player_registration')
    else:
        form = PlayerRegistrationForm()
    return render(request, 'player_registration.html', {'form': form})


def register_tournament(request):
    if request.method == 'POST':
        form = TournamentRegistrationForm(request.POST)
        if form.is_valid():
            new_tournament = form.save()
            messages.success(request, 'Torneio cadastrado com sucesso!')
            return redirect('tournament_results', tournament_id=new_tournament.id)
    else:
        form = TournamentRegistrationForm()
    return render(request, 'tournament_registration.html', {'form': form})


def list_tournaments(request):
    tournaments = Tournament.objects.all()
    return render(request, 'list_tournaments.html', {'tournaments': tournaments})

def view_ranking(request):
    rankings = Ranking.objects.all().order_by('-total_points')
    return render(request, 'ranking.html', {'rankings': rankings})

def tournament_results(request, tournament_id):
    # Obtenha o objeto do torneio
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    # Calcule o número de formulários extras com base no número de jogadores e resultados existentes
    extra_forms = tournament.number_of_players - TournamentResult.objects.filter(tournament=tournament).count()
    extra_forms = max(0, extra_forms)
    
    # Crie o formset com o número correto de formulários extras
    TournamentFormSet = modelformset_factory(
        TournamentResult,
        form=TournamentResultForm,
        extra=extra_forms,
    )

    if request.method == 'POST':
        formset = TournamentFormSet(request.POST, queryset=TournamentResult.objects.filter(tournament=tournament))
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.tournament = tournament
                
                # Verifique se já existe um registro para o mesmo torneio e jogador
                existing_result = TournamentResult.objects.filter(tournament=tournament, player=instance.player).first()
                if existing_result:
                    existing_result.position = instance.position
                    existing_result.points = instance.points
                    existing_result.save()
                else:
                    instance.save()
                
                # Atualize ou crie o ranking do jogador
                ranking, created = Ranking.objects.get_or_create(player=instance.player)
                ranking.add_points(instance.points)
            
            # Não precisamos criar ou atualizar o registro do torneio novamente aqui
            # pois o nome e a data já estão definidos corretamente
            messages.success(request, 'Resultados do torneio salvos com sucesso.')
            return redirect('view_ranking')
    else:
        formset = TournamentFormSet(queryset=TournamentResult.objects.filter(tournament=tournament))

    return render(request, 'tournament_results.html', {'formset': formset, 'tournament': tournament})


def export_rankings_csv(request):
    # Crie uma resposta HTTP com o cabeçalho de conteúdo correto
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rankings.csv"'

    # Crie um escritor CSV usando a resposta HTTP como arquivo
    writer = csv.writer(response)

    # Escreva o cabeçalho do CSV
    writer.writerow(['Posição', 'Nome do Jogador', 'Deck', 'Pontos'])

    # Busque os dados de ranking do seu modelo
    rankings = Ranking.objects.all().order_by('-total_points')

    # Escreva os dados no CSV usando o índice do loop como a posição
    for idx, rank in enumerate(rankings, 1):
        writer.writerow([idx, rank.player.name, 'Deck', rank.total_points])  # Substitua 'Deck' conforme necessário

    # Retorne a resposta HTTP com o CSV
    return response

from .forms import DeckRegistrationForm

def deck_registration(request):
    if request.method == 'POST':
        form = DeckRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deck cadastrado com sucesso!')
            return redirect('view_decks')  # Certifique-se de que o nome da URL está correto
    else:
        form = DeckRegistrationForm()
    return render(request, 'deck_registration.html', {'form': form})


def view_decks(request):
    deck_stats = Deck.objects.annotate(num_players=Count('tournamentresult'))
    total_players = TournamentResult.objects.count()

    if total_players > 0:
        deck_stats = [{'name': deck.name, 'count': deck.num_players, 'percentage': (deck.num_players / total_players) * 100} for deck in deck_stats]
    else:
        deck_stats = [{'name': deck.name, 'count': deck.num_players, 'percentage': 0} for deck in deck_stats]

    return render(request, 'view_decks.html', {'deck_stats': deck_stats})

from django.db.models import Count, Q

def view_players(request):
    players = Player.objects.all()
    player_stats = []

    for player in players:
        weekly_wins = TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='Semanal').count()
        premiere_wins = TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='Premiere').count()
        ots_wins = TournamentResult.objects.filter(player=player, position=1, tournament__tournament_type__name='OTS').count()

        player_stats.append({
            'player': player,
            'weekly_wins': weekly_wins,
            'premiere_wins': premiere_wins,
            'ots_wins': ots_wins
        })

    return render(request, 'view_players.html', {'player_stats': player_stats})


def show_decks(request):
    decks = Deck.objects.all()
    for deck in decks:
        deck.special_info = deck.get_special_info()  # Utilizando o método que você adicionou
    return render(request, 'show_decks.html', {'decks': decks})


def report_decks(request):
    # Obter o torneio mais recente
    latest_tournament = Tournament.objects.order_by('-date').first()
    
    # Obter os resultados do torneio mais recente
    if latest_tournament:
        results = TournamentResult.objects.filter(tournament=latest_tournament).order_by('position')[:10]
    else:
        results = []

    context = {
        'results': results,
        'tournament': latest_tournament  # Passar o torneio mais recente para o contexto
    }
    return render(request, 'report_decks.html', context)

from django.shortcuts import render
from django.http import HttpResponse
from export_functions import (
    export_players_to_firestore,
    export_tournaments_to_firestore,
    export_decks_to_firestore,
    export_rankings_to_firestore
)

def sync_players_view(request):
    export_players_to_firestore()
    return render(request, 'sync_players.html')

def sync_tournaments_view(request):
    export_tournaments_to_firestore()
    return render(request, 'sync_tournaments.html')

def sync_decks_view(request):
    export_decks_to_firestore()
    return render(request, 'sync_decks.html')

def sync_rankings_view(request):
    export_rankings_to_firestore()
    return render(request, 'sync_rankings.html')

def sync_all_view(request):
    export_players_to_firestore()
    export_tournaments_to_firestore()
    export_decks_to_firestore()
    export_rankings_to_firestore()
    return render(request, 'sync_all.html')



