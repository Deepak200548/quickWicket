from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name="logout"),
    path('create_game/', views.create_game, name='createGame'),
    path('begin_game/',views.begin_game,name="beginGame"),
    path('update_game/',views.game_update,name="game_update"),
    path('matches/',views.matches,name="matches"),
    path('players/',views.players_list,name="players"),
    path('undo_data/',views.undo_data,name="undo_data"),
    path('game/<str:game_id>', views.game, name='game'),
    path('game_details/<str:game_id>', views.game_details_json, name='game'),
    path('player/<str:username>',views.player_profile,name="player_profile")
]

