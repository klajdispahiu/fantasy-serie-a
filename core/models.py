from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class SerieATeam(models.Model):
    """A real Serie A club (e.g. Juventus, Inter Milan)"""
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)  # e.g. JUV, INT
    badge_color = models.CharField(max_length=7, default='#000000')  # hex

    def __str__(self):
        return self.name


class Player(models.Model):
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]

    name = models.CharField(max_length=100)
    team = models.ForeignKey(SerieATeam, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    price = models.DecimalField(max_digits=4, decimal_places=1)  # in millions, e.g. 12.5
    total_points = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)  # False if injured/suspended

    def __str__(self):
        return f"{self.name} ({self.team.short_name} - {self.position})"


class Gameweek(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)  # e.g. "Giornata 1"
    deadline = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['number']


class GameweekScore(models.Model):
    """Points a player earned in a specific gameweek"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='gameweek_scores')
    gameweek = models.ForeignKey(Gameweek, on_delete=models.CASCADE, related_name='scores')
    points = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheet = models.BooleanField(default=False)
    yellow_card = models.BooleanField(default=False)
    red_card = models.BooleanField(default=False)
    minutes = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)

    class Meta:
        unique_together = ['player', 'gameweek']

    def __str__(self):
        return f"{self.player.name} - GW{self.gameweek.number}: {self.points}pts"


class Squad(models.Model):
    """A user's fantasy squad"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='squad')
    name = models.CharField(max_length=100)
    budget_remaining = models.DecimalField(max_digits=5, decimal_places=1, default=100.0)
    total_points = models.IntegerField(default=0)
    gameweek_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class SquadPlayer(models.Model):
    """A player within a user's squad, with captain/vice-captain flags"""
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='squad_players')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    is_captain = models.BooleanField(default=False)
    is_vice_captain = models.BooleanField(default=False)
    is_on_bench = models.BooleanField(default=False)  # bench = not scoring this GW

    class Meta:
        unique_together = ['squad', 'player']

    def __str__(self):
        return f"{self.squad.name} — {self.player.name}"


class Transfer(models.Model):
    """A player transfer in or out of a squad"""
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='transfers')
    player_in = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfers_in')
    player_out = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfers_out')
    gameweek = models.ForeignKey(Gameweek, on_delete=models.CASCADE)
    transferred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.squad.name}: {self.player_in.name} IN / {self.player_out.name} OUT"


class League(models.Model):
    """A mini-league users can create and join"""
    name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=8, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leagues')
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class LeagueMembership(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='memberships')
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='league_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['league', 'squad']

    def __str__(self):
        return f"{self.squad.name} in {self.league.name}"