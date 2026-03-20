from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import SerieATeam, Player, Gameweek
from django.utils import timezone
from datetime import timedelta
import random


TEAMS = [
    ("Juventus", "JUV", "#000000"),
    ("Inter Milan", "INT", "#0033CC"),
    ("AC Milan", "MIL", "#CC0000"),
    ("Napoli", "NAP", "#00CCFF"),
    ("AS Roma", "ROM", "#8B0000"),
    ("Lazio", "LAZ", "#87CEEB"),
    ("Atalanta", "ATA", "#0000CD"),
    ("Fiorentina", "FIO", "#6A0DAD"),
    ("Torino", "TOR", "#8B4513"),
    ("Bologna", "BOL", "#CC0000"),
    ("Udinese", "UDI", "#000000"),
    ("Sassuolo", "SAS", "#006400"),
    ("Empoli", "EMP", "#00008B"),
    ("Hellas Verona", "VER", "#FFD700"),
    ("Genoa", "GEN", "#8B0000"),
    ("Cagliari", "CAG", "#CC0000"),
    ("Lecce", "LEC", "#FFD700"),
    ("Frosinone", "FRO", "#FFD700"),
    ("Salernitana", "SAL", "#8B0000"),
    ("Monza", "MON", "#CC0000"),
]

PLAYERS = {
    "JUV": [
        ("Wojciech Szczesny", "GK", 5.5), ("Bremer", "DEF", 6.0),
        ("Danilo", "DEF", 5.5), ("Federico Gatti", "DEF", 4.5),
        ("Manuel Locatelli", "MID", 6.0), ("Adrien Rabiot", "MID", 6.5),
        ("Filip Kostic", "MID", 5.5), ("Dusan Vlahovic", "FWD", 9.0),
        ("Federico Chiesa", "FWD", 8.0), ("Arkadiusz Milik", "FWD", 6.5),
        ("Weston McKennie", "MID", 5.0),
    ],
    "INT": [
        ("Yann Sommer", "GK", 5.5), ("Alessandro Bastoni", "DEF", 6.5),
        ("Francesco Acerbi", "DEF", 5.5), ("Benjamin Pavard", "DEF", 6.0),
        ("Nicolo Barella", "MID", 8.5), ("Hakan Calhanoglu", "MID", 8.0),
        ("Henrikh Mkhitaryan", "MID", 6.0), ("Lautaro Martinez", "FWD", 11.0),
        ("Marcus Thuram", "FWD", 9.0), ("Alexis Sanchez", "FWD", 6.0),
        ("Denzel Dumfries", "DEF", 6.0),
    ],
    "MIL": [
        ("Mike Maignan", "GK", 5.5), ("Theo Hernandez", "DEF", 8.0),
        ("Fikayo Tomori", "DEF", 5.5), ("Davide Calabria", "DEF", 5.0),
        ("Tijjani Reijnders", "MID", 6.5), ("Ruben Loftus-Cheek", "MID", 6.5),
        ("Christian Pulisic", "MID", 7.0), ("Olivier Giroud", "FWD", 8.0),
        ("Rafael Leao", "FWD", 10.0), ("Noah Okafor", "FWD", 5.5),
        ("Yunus Musah", "MID", 5.5),
    ],
    "NAP": [
        ("Alex Meret", "GK", 5.0), ("Giovanni Di Lorenzo", "DEF", 6.5),
        ("Min-jae Kim", "DEF", 7.0), ("Mario Rui", "DEF", 5.0),
        ("Piotr Zielinski", "MID", 7.5), ("Stanislav Lobotka", "MID", 7.0),
        ("Khvicha Kvaratskhelia", "MID", 10.0), ("Victor Osimhen", "FWD", 12.5),
        ("Giacomo Raspadori", "FWD", 7.0), ("Matteo Politano", "MID", 6.0),
        ("Eljif Elmas", "MID", 5.5),
    ],
    "ROM": [
        ("Rui Patricio", "GK", 4.5), ("Roger Ibanez", "DEF", 5.5),
        ("Chris Smalling", "DEF", 6.0), ("Leonardo Spinazzola", "DEF", 5.5),
        ("Lorenzo Pellegrini", "MID", 7.5), ("Bryan Cristante", "MID", 6.0),
        ("Paulo Dybala", "FWD", 9.5), ("Romelu Lukaku", "FWD", 9.0),
        ("Stephan El Shaarawy", "MID", 6.0), ("Tammy Abraham", "FWD", 7.5),
        ("Leandro Paredes", "MID", 5.5),
    ],
}

# Fill remaining teams with generic players
GENERIC_PLAYERS = {
    "GK": [("Goalkeeper A", 4.5), ("Goalkeeper B", 4.0)],
    "DEF": [("Defender A", 5.0), ("Defender B", 4.5), ("Defender C", 4.5), ("Defender D", 4.0)],
    "MID": [("Midfielder A", 6.0), ("Midfielder B", 5.5), ("Midfielder C", 5.0), ("Midfielder D", 5.0)],
    "FWD": [("Forward A", 7.0), ("Forward B", 6.0), ("Forward C", 5.5)],
}


class Command(BaseCommand):
    help = 'Seeds the database with Serie A teams, players, and gameweeks'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding teams...')
        team_map = {}
        for name, short, color in TEAMS:
            team, _ = SerieATeam.objects.get_or_create(
                short_name=short,
                defaults={'name': name, 'badge_color': color}
            )
            team_map[short] = team

        self.stdout.write('Seeding players...')
        for short, players in PLAYERS.items():
            team = team_map[short]
            for player_name, position, price in players:
                Player.objects.get_or_create(
                    name=player_name,
                    team=team,
                    defaults={
                        'position': position,
                        'price': price,
                        'total_points': random.randint(20, 120),
                    }
                )

        # Fill remaining teams with generic players
        remaining = [s for s in team_map if s not in PLAYERS]
        for short in remaining:
            team = team_map[short]
            for position, generic_list in GENERIC_PLAYERS.items():
                for i, (pname, price) in enumerate(generic_list):
                    Player.objects.get_or_create(
                        name=f"{pname} ({team.short_name})",
                        team=team,
                        defaults={
                            'position': position,
                            'price': price,
                            'total_points': random.randint(10, 80),
                        }
                    )

        self.stdout.write('Seeding gameweeks...')
        now = timezone.now()
        for i in range(1, 39):
            Gameweek.objects.get_or_create(
                number=i,
                defaults={
                    'name': f'Giornata {i}',
                    'deadline': now + timedelta(weeks=i - 1),
                    'is_active': i == 1,
                    'is_finished': False,
                }
            )

        self.stdout.write('Creating demo user...')
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@example.com', 'demo1234')

        self.stdout.write(self.style.SUCCESS('Done! Database seeded successfully.'))