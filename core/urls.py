from django.urls import path
from . import views

urlpatterns = [
    path('', views.squad_view, name='squad'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Squad
    path('api/players/', views.players_api, name='players_api'),
    path('api/add-player/', views.add_player, name='add_player'),
    path('api/remove-player/', views.remove_player, name='remove_player'),
    path('api/set-captain/', views.set_captain, name='set_captain'),

    # Transfers
    path('transfers/', views.transfers_view, name='transfers'),
    path('api/transfer/', views.make_transfer, name='make_transfer'),

    # Leagues
    path('leagues/', views.leagues_view, name='leagues'),
    path('leagues/<int:league_id>/', views.league_detail, name='league_detail'),
    path('api/create-league/', views.create_league, name='create_league'),
    path('api/join-league/', views.join_league, name='join_league'),

    # Gameweek
    path('gameweek/', views.gameweek_view, name='gameweek'),
    path('simulate/', views.simulate_gw, name='simulate_gw'),

    path('api/swap-player/', views.swap_player, name='swap_player'),
]