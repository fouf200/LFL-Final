from django.conf.urls import url
from django.urls import path
from myapp import views
from django.contrib import admin
# TEMPLATE TAGGING
app_name = 'myapp'

urlpatterns=[
    url(r'^$', views.home, name="main"),
    url(r'^login', views.login, name="login"),
    url(r'^logout', views.logout, name="logout"),
    url(r'^select', views.select, name="select"),
    url(r'^about', views.about, name="about"),
    url(r'^signup', views.signup, name="signup"),
    url(r'^home_user',views.home_user,name="home_user"),
    url(r'^fixtures_display',views.fixtures_display,name="fixtures_display"),
    url(r'^standings', views.standings, name="standings"),
    path(r'^fixture_details/<int:game_id>/',views.fixture_details,name="fixture_details"),
    url(r'^Standings_list',views.Standings_list,name="Standings_list"),
    url(r'^statistics_search_players', views.statistics_search_players, name="statistics_search_players"),
    url(r'^choose_team', views.choose_team, name="choose_team"),
    url(r'^team_pick', views.pick_team1, name="pick_team1"),
    url(r'^team_section', views.team_section, name="team_section"),
    url(r'player_section', views.enter_player, name = 'player_section'),
	url(r'team_section', views.enter_team, name = 'team_section'),
	url(r'^game_section', views.enter_game, name = 'game_section'),
	url(r'^set_game', views.set_game, name = 'set_game'),
	url(r'^game_modify', views.game_modify, name = 'game_modify'),
	url(r'^game_delete', views.game_delete, name = 'game_delete'),
	url(r'^add_event', views.add_event, name = 'add_event'),
	url(r'^add_player', views.add_player, name='add_player'),
	url(r'^modify_player', views.modify_player, name='modify_player'),
	url(r'^delete_player', views.delete_player, name = 'delete_player'),
	url(r'^add_team', views.add_team, name = 'add_team'),
	url(r'^delete_team', views.delete_team, name = 'delete_team'),
	url(r'^modify_team', views.modify_team, name = 'modify_team'),
	url(r'^advanced_modify_team', views.advanced_modify_team, name = 'advanced_modify_team'),
	url(r'^add_player_team', views.add_player_team, name = 'add_player_team'),
	url(r'^remove_player_team', views.remove_player_team, name = 'remove_player_team'),
    url(r'^add_event', views.add_event, name = 'add_event'),
    url(r'^back_main', views.back_main, name="back_main"),
    url(r'^next_select', views.next_select, name="next_select"),
    url(r'^back2', views.back2, name="back2"),
    url(r'^top_scorers', views.top_scorers, name="top_scorers"),
    url(r'^pick', views.pick_team, name="pick_team")
]
