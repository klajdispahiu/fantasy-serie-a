# ⚽ Fantasy Serie A

> A full-stack fantasy football web application built for the Italian Serie A — because the most passionate league in the world deserves a great fantasy game.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)

---

## 🧠 Why I Built This

I have two great passions in life — **technology** and **football**, specifically Serie A.

Fantasy football has exploded in popularity worldwide. The Premier League has one of the best fantasy platforms out there. La Liga, the Bundesliga, and even the Champions League have solid options. But Serie A — arguably the most tactically rich, historically deep, and passionately followed league in the world — has never had a fantasy app that truly does it justice.

The official Fantacalcio apps that exist are clunky, outdated, or locked behind paywalls. There is nothing clean, modern, and open that captures the real experience of managing a Serie A squad week by week.

So I decided to build one myself. This project combines everything I love: writing clean backend code in Django, building interfaces that feel good to use, and thinking about football in a deeper, more structured way. It is a personal project, a learning project, and hopefully a useful one for any Serie A fan who wants to play fantasy football the right way.

---

## ✨ Features

- **Squad Builder** — Build your 15-player squad on an interactive pitch view with a £100m budget
- **Position Rules** — Enforced limits: 2 GK, 5 DEF, 5 MID, 3 FWD with max 3 players per club
- **Bench Management** — Click to swap any outfield starter with any bench player regardless of position, letting the formation adjust automatically
- **Goalkeeper Rule** — Exactly 1 GK must always start; the second is automatically placed on the bench
- **Captain System** — Assign a captain whose points are doubled each gameweek
- **Transfer Market** — Buy and sell players between gameweeks with a free transfer system
- **Gameweek Scoring** — Points calculated on goals, assists, clean sheets, yellow/red cards, minutes played, and bonus points
- **Gameweek Simulation** — Simulate a full gameweek and generate realistic randomised player scores (development mode)
- **Mini Leagues** — Create or join private leagues with unique invite codes and a live leaderboard
- **User Accounts** — Full registration, login, and session management
- **Admin Panel** — Django admin configured to add, edit, or remove players, teams, and gameweeks with no code needed
- **2025/26 Season Data** — All 20 Serie A clubs and their squads seeded into the database

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.x |
| API | Django REST Framework |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Database | SQLite (development) |
| Authentication | Django built-in auth |
| Fonts | Bebas Neue + DM Sans (Google Fonts) |
| Version Control | Git + GitHub |

---

## 📁 Project Structure

```
fantasy_serie_a/
├── core/
│   ├── models.py                   # All database models
│   ├── views.py                    # Page views and JSON API endpoints
│   ├── urls.py                     # URL routing
│   ├── admin.py                    # Django admin configuration
│   ├── scoring.py                  # Gameweek points engine
│   ├── serializers.py              # DRF serializers
│   └── management/
│       └── commands/
│           └── seed_data.py        # Seeds all 20 Serie A squads
├── static/
│   ├── css/style.css               # Full design system
│   └── js/app.js                   # Global JS utilities
├── templates/
│   ├── base.html                   # Master layout with navbar
│   └── core/
│       ├── squad.html              # Interactive pitch squad builder
│       ├── transfers.html          # Transfer market
│       ├── gameweek.html           # Gameweek scores table
│       ├── leagues.html            # League management
│       ├── league_detail.html      # League leaderboard
│       ├── login.html
│       └── register.html
├── fantasy_serie_a/
│   ├── settings.py
│   └── urls.py
├── .env                            # Secret key — not committed
├── .gitignore
├── README.md
└── manage.py
```

---

## 🚀 Run It Yourself

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/klajdispahiu/fantasy-serie-a.git
cd fantasy-serie-a
```

### Step 2 — Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install django djangorestframework pillow django-cors-headers python-dotenv
```

### Step 4 — Create your .env file

Create a file called `.env` in the project root and add:

```
SECRET_KEY=any-random-string-you-choose
DEBUG=True
```

### Step 5 — Run migrations

```bash
python manage.py migrate
```

### Step 6 — Seed the database

This populates all 20 Serie A clubs, their squads, and 38 gameweeks:

```bash
python manage.py seed_data
```

### Step 7 — Create an admin account (optional)

```bash
python manage.py createsuperuser
```

### Step 8 — Start the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` and register your account to start building your squad.

The admin panel is available at `http://127.0.0.1:8000/admin/`

---

## 🎮 How to Play

### Building your squad
1. Register an account and choose your team name
2. Go to **My Squad** and click **Add GK / DEF / MID / FWD** to open the player selection modal
3. Filter by position and price, search by name, and click **+** to add
4. You start with a £100m budget — spend it wisely

### Managing your bench
1. Click any player on the pitch to select them (they glow gold)
2. Valid swap targets on the bench glow green
3. Click a green player to complete the swap
4. Outfield players can swap with any position — the formation adjusts automatically
5. Goalkeepers can only swap with the other goalkeeper

### Setting your captain
Click the 👑 icon on any player card — their points will be doubled that gameweek

### Making transfers
1. Go to **Transfers**
2. Click a player in your squad on the left to select them for sale
3. Browse the market on the right and click **Sign** to complete the deal
4. You get 1 free transfer per gameweek

### Simulating a gameweek
Click **⚡ Simulate Gameweek** on your squad page to generate randomised scores for all players and update every squad's points total

### Leagues
1. Go to **Leagues** and click **Create a League**
2. Share the invite code with friends
3. They paste it under **Join a League**
4. Track the live standings inside each league

---

## 🧮 Scoring System

| Action | GK | DEF | MID | FWD |
|---|---|---|---|---|
| Playing 60+ minutes | +2 | +2 | +2 | +2 |
| Playing 1–59 minutes | +1 | +1 | +1 | +1 |
| Goal scored | +10 | +6 | +5 | +4 |
| Assist | +3 | +3 | +3 | +3 |
| Clean sheet | +6 | +4 | +1 | — |
| Yellow card | −1 | −1 | −1 | −1 |
| Red card | −3 | −3 | −3 | −3 |
| Bonus points | +1/2/3 | +1/2/3 | +1/2/3 | +1/2/3 |
| Captain multiplier | ×2 | ×2 | ×2 | ×2 |

---

## 🗺️ What's Next

- [ ] Connect to a live Serie A data API for real player statistics
- [ ] Automatic weekly gameweek processing with Celery
- [ ] Player price changes based on ownership and form
- [ ] Last 5 gameweeks form indicator on player cards
- [ ] Chip system — Wildcard, Triple Captain, Bench Boost
- [ ] Global overall leaderboard across all users
- [ ] Mobile layout improvements
- [ ] Email notifications for gameweek results

---

## 🔑 Demo Account

A demo account is seeded automatically when you run `seed_data`:

| | |
|---|---|
| Username | `demo` |
| Password | `demo1234` |

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🙏 A Note

This started as a personal project to learn Django properly and to build something I actually wanted to use. Serie A is one of the best leagues in the world and it deserves better than what currently exists for fantasy football. If you are a Serie A fan and a developer, feel free to fork this, improve it, and make it your own.

*Forza il calcio italiano.*
