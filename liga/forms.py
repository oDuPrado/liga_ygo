from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Player, Tournament, TournamentType, TournamentResult, Deck

def validate_length(value):
    if len(value) < 6:
        raise ValidationError(_('ID deve ter pelo menos 6 caracteres.'), params={'value': value})

def validate_non_numeric(value):
    if not value.isnumeric():
        raise ValidationError(_('Contato deve conter apenas números.'), params={'value': value})

class PlayerRegistrationForm(forms.ModelForm):
    official_id = forms.CharField(validators=[validate_length])
    contact = forms.CharField(validators=[validate_non_numeric])

    class Meta:
        model = Player
        fields = ['official_id', 'name', 'contact']
        labels = {
            'official_id': 'ID Oficial',
            'name': 'Nome',
            'contact': 'Contato',
        }

class TournamentRegistrationForm(forms.ModelForm):
    tournament_type = forms.ModelChoiceField(
        queryset=TournamentType.objects.all(),
        empty_label="Selecione o Tipo",
        label="Tipo de Torneio"
    )

    class Meta:
        model = Tournament
        fields = ['date', 'tournament_type', 'number_of_players']
        widgets = {
            'date': forms.DateInput(format='%d/%m/%Y', attrs={'type': 'date'}),
        }
        labels = {
            'date': 'Data do Torneio',
            'number_of_players': "Número de Jogadores",
            'tournament_type': "Tipo de Torneio"
        }

class TournamentRankingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        players = kwargs.pop('players', Player.objects.none())
        super().__init__(*args, **kwargs)
        for i, player in enumerate(players):
            self.fields[f'ranking_{i+1}'] = forms.ModelChoiceField(
                queryset=Player.objects.all(),
                label=f'{i+1}º lugar',
                required=False
            )
            self.fields[f'points_{i+1}'] = forms.IntegerField(
                label=f'Pontos para {i+1}º lugar',
                required=False
            )

class TournamentResultForm(forms.ModelForm):
    deck = forms.ModelChoiceField(
        queryset=Deck.objects.all(),
        empty_label="Selecione o Deck",
        label="Deck"
    )

    class Meta:
        model = TournamentResult
        fields = ['player', 'position', 'points', 'deck']

class DeckRegistrationForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['name', 'image']
        labels = {
            'name': 'Nome do Deck',
            'image': 'Imagem do Deck',
        }
