from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json, random, string

from .models import (
    Player, Squad, SquadPlayer, Gameweek, GameweekScore,
    League, LeagueMembership, Transfer, SerieATeam
)
from .scoring import simulate_gameweek, update_squad_points


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        squad_name = request.POST['squad_name']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'core/register.html')
        user = User.objects.create_user(username=username, password=password)
        Squad.objects.create(user=user, name=squad_name)
        login(request, user)
        return redirect('squad')
    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('squad')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Squad ─────────────────────────────────────────────────────────────────────

@login_required
def squad_view(request):
    squad = get_object_or_404(Squad, user=request.user)
    squad_players = squad.squad_players.select_related('player__team').all()
    gameweek = Gameweek.objects.filter(is_active=True).first()
    context = {
        'squad': squad,
        'squad_players': squad_players,
        'gameweek': gameweek,
        'positions': ['GK', 'DEF', 'MID', 'FWD'],
    }
    return render(request, 'core/squad.html', context)


@login_required
def players_api(request):
    """Returns all available players as JSON for the squad builder."""
    position = request.GET.get('position', '')
    team_id = request.GET.get('team', '')
    max_price = request.GET.get('max_price', 15)

    players = Player.objects.filter(is_available=True).select_related('team')
    if position:
        players = players.filter(position=position)
    if team_id:
        players = players.filter(team_id=team_id)
    players = players.filter(price__lte=max_price).order_by('-total_points')

    squad = get_object_or_404(Squad, user=request.user)
    owned_ids = set(squad.squad_players.values_list('player_id', flat=True))

    data = [{
        'id': p.id,
        'name': p.name,
        'team': p.team.name,
        'team_short': p.team.short_name,
        'team_color': p.team.badge_color,
        'position': p.position,
        'price': float(p.price),
        'total_points': p.total_points,
        'owned': p.id in owned_ids,
    } for p in players]
    return JsonResponse({'players': data})


@login_required
@require_POST
def add_player(request):
    data = json.loads(request.body)
    player_id = data.get('player_id')
    player = get_object_or_404(Player, id=player_id)
    squad = get_object_or_404(Squad, user=request.user)

    # Validation
    if squad.squad_players.count() >= 15:
        return JsonResponse({'error': 'Squad is full (15 players max).'}, status=400)
    if squad.budget_remaining < player.price:
        return JsonResponse({'error': 'Insufficient budget.'}, status=400)
    if squad.squad_players.filter(player=player).exists():
        return JsonResponse({'error': 'Player already in squad.'}, status=400)

    # Max 3 players per real team
    team_count = squad.squad_players.filter(player__team=player.team).count()
    if team_count >= 3:
        return JsonResponse({'error': f'Max 3 players from {player.team.name}.'}, status=400)

    # Position limits: 2 GK, 5 DEF, 5 MID, 3 FWD
    pos_limits = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
    pos_count = squad.squad_players.filter(player__position=player.position).count()
    if pos_count >= pos_limits[player.position]:
        return JsonResponse({'error': f'Max {pos_limits[player.position]} {player.position}s allowed.'}, status=400)

    with transaction.atomic():
        SquadPlayer.objects.create(squad=squad, player=player, is_on_bench=squad.squad_players.count() >= 11)
        squad.budget_remaining -= player.price
        squad.save()

    return JsonResponse({'success': True, 'budget_remaining': float(squad.budget_remaining)})


@login_required
@require_POST
def remove_player(request):
    data = json.loads(request.body)
    sp = get_object_or_404(SquadPlayer, id=data.get('squad_player_id'), squad__user=request.user)
    with transaction.atomic():
        squad = sp.squad
        squad.budget_remaining += sp.player.price
        squad.save()
        sp.delete()
    return JsonResponse({'success': True, 'budget_remaining': float(squad.budget_remaining)})


@login_required
@require_POST
def set_captain(request):
    data = json.loads(request.body)
    squad = get_object_or_404(Squad, user=request.user)
    squad.squad_players.update(is_captain=False, is_vice_captain=False)
    sp = get_object_or_404(SquadPlayer, id=data.get('squad_player_id'), squad=squad)
    sp.is_captain = True
    sp.save()
    return JsonResponse({'success': True})


# ── Transfers ─────────────────────────────────────────────────────────────────

@login_required
def transfers_view(request):
    squad = get_object_or_404(Squad, user=request.user)
    gameweek = Gameweek.objects.filter(is_active=True).first()
    transfers_this_gw = Transfer.objects.filter(squad=squad, gameweek=gameweek).count() if gameweek else 0
    context = {
        'squad': squad,
        'gameweek': gameweek,
        'transfers_used': transfers_this_gw,
        'free_transfers': max(0, 1 - transfers_this_gw),
    }
    return render(request, 'core/transfers.html', context)


@login_required
@require_POST
def make_transfer(request):
    data = json.loads(request.body)
    player_in = get_object_or_404(Player, id=data.get('player_in_id'))
    squad_player_out = get_object_or_404(SquadPlayer, id=data.get('squad_player_out_id'), squad__user=request.user)
    player_out = squad_player_out.player
    squad = squad_player_out.squad
    gameweek = Gameweek.objects.filter(is_active=True).first()

    if not gameweek:
        return JsonResponse({'error': 'No active gameweek.'}, status=400)
    if player_in.position != player_out.position:
        return JsonResponse({'error': 'Positions must match.'}, status=400)

    budget_after = squad.budget_remaining + player_out.price - player_in.price
    if budget_after < 0:
        return JsonResponse({'error': 'Insufficient budget for this transfer.'}, status=400)

    with transaction.atomic():
        squad_player_out.player = player_in
        squad_player_out.save()
        squad.budget_remaining = budget_after
        squad.save()
        Transfer.objects.create(squad=squad, player_in=player_in, player_out=player_out, gameweek=gameweek)

    return JsonResponse({'success': True, 'budget_remaining': float(squad.budget_remaining)})


# ── Leagues ───────────────────────────────────────────────────────────────────

@login_required
def leagues_view(request):
    squad = get_object_or_404(Squad, user=request.user)
    my_leagues = League.objects.filter(memberships__squad=squad)
    return render(request, 'core/leagues.html', {'squad': squad, 'my_leagues': my_leagues})


@login_required
@require_POST
def create_league(request):
    data = json.loads(request.body)
    squad = get_object_or_404(Squad, user=request.user)
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    league = League.objects.create(name=data['name'], invite_code=code, created_by=request.user)
    LeagueMembership.objects.create(league=league, squad=squad)
    return JsonResponse({'success': True, 'invite_code': code})


@login_required
@require_POST
def join_league(request):
    data = json.loads(request.body)
    squad = get_object_or_404(Squad, user=request.user)
    league = get_object_or_404(League, invite_code=data['invite_code'])
    if LeagueMembership.objects.filter(league=league, squad=squad).exists():
        return JsonResponse({'error': 'Already a member.'}, status=400)
    LeagueMembership.objects.create(league=league, squad=squad)
    return JsonResponse({'success': True, 'league_name': league.name})


@login_required
def league_detail(request, league_id):
    league = get_object_or_404(League, id=league_id)
    memberships = league.memberships.select_related('squad__user').order_by('-squad__total_points')
    return render(request, 'core/league_detail.html', {'league': league, 'memberships': memberships})


# ── Gameweek ──────────────────────────────────────────────────────────────────

@login_required
def gameweek_view(request):
    gameweek = Gameweek.objects.filter(is_active=True).first()
    scores = []
    if gameweek:
        scores = GameweekScore.objects.filter(gameweek=gameweek).select_related('player__team').order_by('-points')[:20]
    return render(request, 'core/gameweek.html', {'gameweek': gameweek, 'scores': scores})


@login_required
def simulate_gw(request):
    """Dev-only view to simulate a gameweek and generate scores."""
    gameweek = Gameweek.objects.filter(is_active=True).first()
    if gameweek:
        simulate_gameweek(gameweek)
        update_squad_points(gameweek)
        gameweek.is_finished = True
        gameweek.is_active = False
        gameweek.save()
        next_gw = Gameweek.objects.filter(number=gameweek.number + 1).first()
        if next_gw:
            next_gw.is_active = True
            next_gw.save()
        messages.success(request, f'{gameweek.name} simulated! Scores updated.')
    return redirect('gameweek')

@login_required
@require_POST
def swap_player(request):
    """Swap a starter with a bench player."""
    data = json.loads(request.body)
    squad = get_object_or_404(Squad, user=request.user)
    starter_sp = get_object_or_404(SquadPlayer, id=data.get('starter_id'), squad=squad)
    bench_sp = get_object_or_404(SquadPlayer, id=data.get('bench_id'), squad=squad)

    if starter_sp.player.position != bench_sp.player.position:
        return JsonResponse({'error': 'You can only swap players of the same position.'}, status=400)

    # Swap their bench status
    starter_sp.is_on_bench = True
    bench_sp.is_on_bench = False
    starter_sp.save()
    bench_sp.save()

    return JsonResponse({'success': True})