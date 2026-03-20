from .models import GameweekScore, SquadPlayer, Squad, Gameweek
import random


POINTS = {
    'GK': {'goal': 10, 'assist': 3, 'clean_sheet': 6, 'yellow': -1, 'red': -3, 'per_minute': 0},
    'DEF': {'goal': 6, 'assist': 3, 'clean_sheet': 4, 'yellow': -1, 'red': -3, 'per_minute': 0},
    'MID': {'goal': 5, 'assist': 3, 'clean_sheet': 1, 'yellow': -1, 'red': -3, 'per_minute': 0},
    'FWD': {'goal': 4, 'assist': 3, 'clean_sheet': 0, 'yellow': -1, 'red': -3, 'per_minute': 0},
}


def calculate_player_points(gw_score, position):
    pts = POINTS[position]
    total = 0
    if gw_score.minutes >= 60:
        total += 2
    elif gw_score.minutes >= 1:
        total += 1
    total += gw_score.goals * pts['goal']
    total += gw_score.assists * pts['assist']
    if gw_score.clean_sheet:
        total += pts['clean_sheet']
    if gw_score.yellow_card:
        total += pts['yellow']
    if gw_score.red_card:
        total += pts['red']
    total += gw_score.bonus
    return max(total, 0)


def simulate_gameweek(gameweek):
    """Generate random scores for all players for a given gameweek (mock mode)."""
    from .models import Player
    for player in Player.objects.filter(is_available=True):
        played = random.random() > 0.2
        minutes = random.randint(60, 90) if played else random.randint(0, 45)
        goals = 0
        if played:
            if player.position == 'FWD':
                goals = random.choices([0, 1, 2, 3], weights=[55, 28, 12, 5])[0]
            elif player.position == 'MID':
                goals = random.choices([0, 1, 2], weights=[70, 22, 8])[0]
            elif player.position == 'DEF':
                goals = random.choices([0, 1], weights=[88, 12])[0]
        assists = random.choices([0, 1, 2], weights=[70, 22, 8])[0] if played else 0
        clean_sheet = random.random() > 0.6 if player.position in ['GK', 'DEF'] else False
        yellow = random.random() > 0.9
        red = random.random() > 0.98

        gw_score, _ = GameweekScore.objects.update_or_create(
            player=player,
            gameweek=gameweek,
            defaults={
                'goals': goals, 'assists': assists,
                'clean_sheet': clean_sheet, 'yellow_card': yellow,
                'red_card': red, 'minutes': minutes,
                'bonus': random.choices([0, 1, 2, 3], weights=[60, 20, 14, 6])[0],
            }
        )
        gw_score.points = calculate_player_points(gw_score, player.position)
        gw_score.save()

        # Update player season totals
        player.total_points += gw_score.points
        player.goals_scored += goals
        player.assists += assists
        player.minutes_played += minutes
        if yellow:
            player.yellow_cards += 1
        if red:
            player.red_cards += 1
        player.save()


def update_squad_points(gameweek):
    """Recalculate all squads' points after gameweek scores are in."""
    for squad_player in SquadPlayer.objects.filter(is_on_bench=False).select_related('player', 'squad'):
        try:
            gw_score = GameweekScore.objects.get(
                player=squad_player.player,
                gameweek=gameweek
            )
        except GameweekScore.DoesNotExist:
            continue

        pts = gw_score.points
        if squad_player.is_captain:
            pts *= 2

        squad = squad_player.squad
        squad.gameweek_points += pts
        squad.total_points += pts
        squad.save()