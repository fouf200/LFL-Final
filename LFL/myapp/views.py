from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from .models import Players,Event,Game,Team,Accounts,StandingTable
from django import forms
from django.contrib import messages
from datetime import date,datetime,time
from django.utils.dateparse import parse_date
from datetime import timedelta
# Create your views here.
def home(request):
    return render(request, 'myapp/main.html')

def login(request):
    if request.method == "POST":
        try:
            newUser=Accounts.objects.get(email=request.POST['email'], password1= request.POST["password"])
            request.session['email'] = newUser.email
            if newUser.email== "admin@gmail.com":
                messages.success(request, "Welcome Admin!")
                return render(request, 'myapp/home_admin.html')

            else:
                messages.success(request, "You're now logged in!")
                return render(request, 'myapp/select.html')

        except Accounts.DoesNotExist as e:
            messages.success(request, 'Login  failed, invalid email or password ')
    return render (request, 'myapp/login.html')

def home_user(request):
    return render(request,'myapp/home_user.html')

def select(request):
    return render(request,'myapp/select.html')
def signup(request):
    if request.method == 'POST':
        name= request.POST['name']
        email = request.POST['email_signup']
        password1 = request.POST['pass']
        password2 = request.POST['re_pass']
        if Accounts.objects.filter(email=email).count() > 0:
            messages.success(request, 'Email already used')
            return render (request, 'myapp/login.html')
        else:
             Accounts(name=name, email=email, password1=password1, password2=password2).save()
             messages.success(request, "Registered!")
             return render(request, 'myapp/signup.html')
    else:
        return render(request, 'myapp/signup.html')

def logout(request):
    try:
        del request.session['email']
        return render(request, 'myapp/main.html')
    except:
        return render (request, 'myapp/main.html')

def about(request):
    return render(request, 'myapp/about.html')

def choose_team(request):
    teams_list = Team.objects.all()
    email = request.session['email']
    fav_team = Accounts.objects.get(email=email)
    if request.method =='POST':
        selected_team=Team.objects.get(team_name=request.POST['team_fav'])
        email = request.session['email']
        Accounts.objects.filter(email=email).update(favorite_team = selected_team)
        messages.success(request, "Team successfully chosen!")
        fav_team = Accounts.objects.get(email=email)
        return render(request, 'myapp/chooseteam.html', {'teams_list':teams_list, 'selected_team':selected_team,'fav_team':fav_team.favorite_team})
    else:
        return render(request, 'myapp/chooseteam.html', {'teams_list':teams_list, 'fav_team':fav_team.favorite_team})

def standings(request):
    standing_table=[]
    standings=list(StandingTable.objects.all().order_by('-PointsAccumulated'))
    r=1
    for s in standings:
        StandingTable.objects.filter(Team=s.Team).update(Ranking=r)
        r+=1
    return render(request, 'myapp/standing_display.html',{'standing_table':standings})

def fixtures_display(request):
    fixtures= Game.objects.all().order_by('game_date')
    temp=[]
    fixtures_list=[]
    if(fixtures):
        last_one=fixtures[0]
    for game in fixtures:
        if game.game_date==last_one.game_date:
            temp.append(game)
        else:
            fixtures_list.append(temp)
            temp=[]
            temp.append(game)
            last_one=game
    if (temp):
        fixtures_list.append(temp)
    try:
        user_email=request.session['email']
        user=Accounts.objects.get(email=user_email)
        favorite_team=user.favorite_team
        favorite_games=Game.objects.filter(team1_id=favorite_team)
        favorite_games.union(Game.objects.filter(team2_id=favorite_team))
        return render(request,'myapp/fixtures_display.html',{'fixtures_list':fixtures_list, 'favorite_games':favorite_games})
    except KeyError:
        return render(request,'myapp/fixtures_display.html',{'fixtures_list':fixtures_list})

    return render(request,'myapp/fixtures_display.html',{'fixtures_list':fixtures_list})

def fixture_details(request,game_id):
    game=Game.objects.get(pk=game_id)
    if game.ended==1:
        score1=game.team1_score
        score2=game.team2_score
    else:
        score1='-'
        score2='-'
    team1_players=list(Players.objects.filter(team=game.team1_id))
    team2_players=list(Players.objects.filter(team=game.team2_id))
    t1=len(team1_players)
    t2=len(team2_players)
    total_players=[]
    largest=max(t1,t2)
    for i in range (0,largest):
        temp=[]
        if(i<t1) and (i<t2):
            temp.append(team1_players[i].name)
            temp.append(team2_players[i].name)
        elif i<t1 or i<t2:
            if i<t1:
                temp.append(team1_players[i].name)
                temp.append("")
            else:
                temp.append("")
                temp.append(team2_players[i].name)
        total_players.append(temp)
    status=""
    if(game.ended==1):
        status="GAME ENDED"
    else:
        status="GAME ONGOING"
    events=Event.objects.filter(game_id=game)
    return render(request,'myapp/game_info.html',{'game':game, 'score1':score1,'score2':score2,'total_players':total_players,'events':events,'status':status})

def Standings_list(request):
    Standings= StandingTable.objects.all().order_by('-Points','-GD')
    return render(request,'myapp/Standings_list.html', {'Standing':Standings})

def pick_team(request):
    Teams_list = Team.objects.all()
    if request.method =="POST":
        selected_team = request.POST['team_fav']
        sel_team=Team.objects.get(team_name=selected_team)
        Players_list=Players.objects.filter(team=sel_team)
        return render(request, 'myapp/chooseplayer.html', {'Players_list':Players_list})
    else:
        return render(request, 'myapp/choose_for_display.html', {'Teams_list':Teams_list})

def statistics_search_players(request):
    if request.method == "POST":
        searched = request.POST['player_fav']
        pl = Players.objects.get(name=searched)
        dateStart = request.POST['dateStart']
        dateEnd = request.POST['dateEnd']
        ev = Event.objects.filter(event_date__lte=dateEnd, event_date__gt=dateStart, player_id=pl)
        numberOfGoals=0
        numberOfAssists=0
        numberOfYellowCards=0
        numberOfRedCards=0
        for i in ev:
            if (i.event_type == "Goal1" or i.event_type == "Goal2"):
                numberOfGoals+=1
            if ((i.event_type).lower == "assist"):
                numberOfAssists+=1
            if ((i.event_type).lower == "red"):
                numberOfYellowCards+=1
            if ((i.event_type).lower == "yellow"):
                numberOfRedCards+=1
        stats = request.POST['stats']
        dateStart = parse_date(dateStart)
        dateEnd = parse_date(dateEnd)
        if(dateStart>dateEnd):
            messages.success(request, 'Date Start cannot be Greater than Date End!')
            Teams_list = Team.objects.all()
            return render(request, 'myapp/chooseTeamForStat.html', {'Teams_list':Teams_list})
        d = dateEnd - dateStart
        days = d.days
        weeks = days/7
        months = days/30
        if(weeks==0):
            weeks+=1
        if(months==0):
            months+=1
        if (stats == "weekly"):
            no_goals= int(numberOfGoals/weeks)
            no_assists = int(numberOfAssists/weeks)
            no_yellowCards = int(numberOfYellowCards/weeks)
            no_redCard = int(numberOfRedCards/weeks)
        if (stats == "monthly"):
            no_goals = int(numberOfGoals/months)
            no_assists = int(numberOfAssists/months)
            no_yellowCards = int(numberOfYellowCards/months)
            no_redCard = int(numberOfRedCards/months)
        return render(request, 'myapp/statistics_results_player.html', {'searched':searched, 'dateStart':dateStart, 'dateEnd':dateEnd, 'no_goals':no_goals, 'no_assists':no_assists, 'no_redCard':no_redCard, 'no_yellowCards':no_yellowCards , 'numberOfGoals':numberOfGoals, 'numberOfAssists':numberOfAssists, 'numberOfYellowCards':numberOfYellowCards, 'numberOfRedCards':numberOfRedCards, 'stats':stats})
    else:
        Teams_list = Team.objects.all()
        return render(request, 'myapp/chooseTeamForStat.html', {'Teams_list':Teams_list})

def next_select(request):
    return render(request, 'myapp/select2.html')
def top_scorers(request):
    players=Players.objects.all().order_by('-goals')
    return render(request,'myapp/top_scorers.html', {'players':players})
def pick_team(request):
    if request.method=='POST':
        team_to_display=request.POST['team_fav']
        team=Team.objects.get(team_name=team_to_display)
        players=Players.objects.filter(team=team)
        return render(request,'myapp/show_team.html',{'team':team,'players':players})
    Teams_list=Team.objects.all()
    return render(request,'myapp/choose_for_display.html',{'Teams_list':Teams_list})

def pick_team1(request):
    Teams_list = Team.objects.all()
    if request.method =="POST":
        selected_team = request.POST['team_fav']
        sel_team=Team.objects.get(team_name=selected_team)
        Players_list=Players.objects.filter(team=sel_team)
        return render(request, 'myapp/chooseplayer.html', {'Players_list':Players_list})
    else:
        return render(request, 'myapp/chooseTeamForStat.html', {'Teams_list':Teams_list})

def back2(request):
    return render(request, 'myapp/select.html')
#################### ADMIN SECTION #################
def enter_player(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    Players_list = Players.objects.all()
    return render(request, 'myapp/player_section.html', {'Players_list':Players_list})

def enter_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    Teams_list= Team.objects.all()
    return render(request, 'myapp/team_section.html', {'Teams_list':Teams_list})

def enter_game(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    games_list = Game.objects.all()
    return render(request, 'myapp/game_section.html',{'games_list':games_list})

def set_game(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    teams_list= Team.objects.all()
    locations = Team.objects.only('location')
    if request.method == 'POST':
        team_home = request.POST['team_home']
        team_visitor = request.POST['team_visitor']
        game_date = request.POST['game_date']
        location = request.POST['game_location']
        if team_home == team_visitor:
            messages.success(request, 'Home Team is equal to Visitor Team, select again')
            return render (request, 'myapp/set_game.html', {'teams_list':teams_list, 'locations_list':locations})

        else:
            try:
                team1=Team.objects.get(team_name=team_home)
                team2=Team.objects.get(team_name=team_visitor)
                if location=="":
                    messages.success(request, "Select a location!")
                    return render(request, 'myapp/set_game.html', {'teams_list':teams_list, 'locations_list':locations})
                Game(team1_id=team1, team2_id=team2, game_date=game_date, location=location).save()
                messages.success(request, "Game registered!")
                return render(request, 'myapp/set_game.html', {'teams_list':teams_list,'locations_list':locations})
            except Team.DoesNotExist as e:
                messages.success(request, 'Select the two teams')
                return render(request, 'myapp/set_game.html', {'teams_list':teams_list,'locations_list':locations})
    else:
        return render(request, 'myapp/set_game.html', {'teams_list':teams_list, 'locations_list':locations})

def game_modify(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    return render(request, 'myapp/game_modify.html')
def game_delete(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    games_list = Game.objects.all()
    if request.method == 'POST':
        game = request.POST['game_delete']
        try:
            game_to_delete=Game.objects.get(pk=game)
        except Game.DoesNotExist as e:
            messages.success(request, "Error!")
            return render(request, 'myapp/game_delete.html', {'games_list':games_list})
        game_to_delete.delete()
        messages.success(request, "Game successfully deleted!")
        return render(request, 'myapp/game_delete.html', {'games_list':games_list})
    else:
        return render(request, 'myapp/game_delete.html', {'games_list':games_list})

def add_event(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    t=datetime.now()
    t_threshold=t+timedelta(minutes=-130)
    games_list=Game.objects.filter(game_date__lte=t,game_date__gte=t_threshold,ended=0)
    if request.method == 'POST' and "set_player" in request.POST:
        temp = request.POST['game_selection']
        game=Game.objects.get(pk=temp)
        team1=game.team1_id
        team2=game.team2_id
        players_list=list(Players.objects.filter(team=team1))
        players_list=players_list+list(Players.objects.filter(team=team2))
        return render(request, 'myapp/add_event_advanced.html', {'game':game,'players_list':players_list})
    elif request.method =='POST' and "end_game" in request.POST:
        temp = request.POST['game_selection']
        game=Game.objects.get(pk=temp)
        team1=game.team1_id
        team2=game.team2_id
        s1=StandingTable.objects.get(pk=team1)
        s2=StandingTable.objects.get(pk=team2)
        t1_p=0
        t2_p=0
        if game.team1_score > game.team2_score:
            t1_p=3
            StandingTable.objects.filter(Team=team1).update(Win=s1.Win+1, Goals=s1.Goals+game.team1_score)
            StandingTable.objects.filter(Team=team2).update(Loss=s2.Loss+1, Goals=s2.Goals+game.team2_score)
        elif game.team1_score == game.team2_score:
            t1_p=1
            t2_p=1
            StandingTable.objects.filter(Team=team1).update(Draw=s1.Draw+1, Goals=s1.Goals+game.team1_score)
            StandingTable.objects.filter(Team=team2).update(Draw=s2.Draw+1, Goals=s2.Goals+game.team2_score)
        else:
            t2_p=3
            StandingTable.objects.filter(Team=team1).update(Loss=s1.Loss+1, Goals=s1.Goals+game.team1_score)
            StandingTable.objects.filter(Team=team2).update(Loss=s2.Win+1, Goals=s2.Goals+game.team2_score)

        StandingTable.objects.filter(Team=team1).update(Played=s1.Played+1,PointsAccumulated=s1.PointsAccumulated+t1_p)
        StandingTable.objects.filter(Team=team2).update(Played=s2.Played+1,PointsAccumulated=s2.PointsAccumulated+t2_p)
        Game.objects.filter(game_id=game.game_id).update(ended=1)


        games_list=Game.objects.filter(game_date__lte=t,game_date__gte=t_threshold,ended=0)
        return render(request, 'myapp/add_event.html',{'games_list':games_list})
    elif request.method == 'POST' and "set_event" in request.POST:
        p = request.POST['player_selection']
        type=request.POST['type_selection']
        game_id=request.POST['game_id']
        game=Game.objects.get(pk=game_id)
        player=Players.objects.get(pk=p)
        if type=='red':
            red=player.red_cards
            Players.objects.filter(pk=p).update(red_cards=red+1)
        elif type=='yellow':
            yellow=player.red_cards
            Players.objects.filter(pk=p).update(yellow_cards=yellow+1)
        elif type=='assist':
            assist=player.assist
            Players.objects.filter(pk=p).update(assist=assist+1)
        elif type=='Goal1':
            t1=game.team1_score
            Game.objects.filter(pk=game_id).update(team1_score=t1+1)
            Players.objects.filter(pk=p).update(goals=player.goals+1)
        elif type=='Goal2':
            t2=game.team2_score
            Game.objects.filter(pk=game_id).update(team2_score=t2+1)
            Players.objects.filter(pk=p).update(goals=player.goals+1)
        at_minute=(datetime.now()-game.game_date.replace(tzinfo=None))
        at_minute=int(at_minute.total_seconds()/60)
        Event(event_type=type,game_id=game,event_date=datetime.now(),minute=at_minute,player_id=player).save()
        messages.success(request, "Event successfully added!")
        return render(request, 'myapp/add_event.html',{'games_list':games_list})
    else:
        return render(request, 'myapp/add_event.html',{'games_list':games_list})

def add_player(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    Players_list= Players.objects.all()
    teams_list = Team.objects.all()
    if request.method == 'POST':
    	player_name= request.POST['player_name']
    	player_team = request.POST['player_teams']
    	player_position = request.POST['player_position']
    	if Players.objects.filter(name=player_name).count() > 0:
    		messages.success(request, 'Player already registered!')
    		return render (request, 'myapp/add_player.html', {'team_list':teams_list})
    	else:
            try:
                player_team1 = Team.objects.get(team_name = player_team)
                Players(name=player_name, team = player_team1, position = player_position).save()
                messages.success(request, "Player registered!")
                return render(request, 'myapp/add_player.html', {'team_list':teams_list})
            except Team.DoesNotExist as e:
                messages.success(request, 'Specify a Team!')
                return render(request, 'myapp/add_player.html', {'team_list':teams_list})
    else:
    	return render(request, 'myapp/add_player.html', {'team_list':teams_list})

def modify_player(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    return render(request, 'myapp/modify_player.html')

def delete_player(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    players_list = Players.objects.all()
    if request.method =='POST':
        try:
            selected_player=Players.objects.get(name=request.POST['player_delete'])
            selected_player.delete()
            messages.success(request, "Player successfully deleted!")
            return render(request, 'myapp/delete_player.html', {'players_list':players_list})
        except Players.DoesNotExist as e:
            messages.success(request, 'Player does not exist, please try again!')
    return render (request, 'myapp/delete_player.html',{'players_list':players_list})

def add_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    Teams_list= Team.objects.all()
    if request.method == 'POST':
        team_name= request.POST['team_name']
        team_president = request.POST['team_president']
        team_coach = request.POST['team_coach']
        location = request.POST['team_location']

        if Team.objects.filter(team_name=team_name).count() > 0:
            messages.success(request, 'Team already registered!')
            return render (request, 'myapp/createteam.html')

        else:
            x=Team(team_name=team_name, team_president=team_president, team_coach=team_coach, location=location).save()
            StandingTable(Team=x).save()
            messages.success(request, "Team registered!")
            return render(request, 'myapp/createteam.html')
    else:
        return render(request, 'myapp/createteam.html')

def modify_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    team_list = Team.objects.all()
    if request.method == 'POST':
        try:
            selected_team=Team.objects.get(team_name=request.POST['player_teams'])
            return render(request, 'myapp/modify_team_advanced.html', {'selected_team':selected_team})
        except Team.DoesNotExist as e:
            messages.success(request, 'Please Select a Team!')
            return render(request, 'myapp/modify_team.html',{'team_list':team_list})
    else:
        return render(request, 'myapp/modify_team.html',{'team_list':team_list})

def delete_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    teams_list = Team.objects.all()
    if request.method =='POST':
        try:
            selected_team=Team.objects.get(team_name=request.POST['team_delete'])
            selected_team.delete()
            messages.success(request, "Team successfully deleted!")
            return render(request, 'myapp/deleteteam.html', {'teams_list':teams_list})
        except Team.DoesNotExist as e:
            messages.success(request, 'Team does not exist, please try again!')
    return render (request, 'myapp/deleteteam.html',{'teams_list':teams_list})

def advanced_modify_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    team_list = Team.objects.all()
    if request.method =='POST':
    	original=request.POST['original']
    	new_name=request.POST['team_name']
    	if Team.objects.filter(team_name=new_name).count() > 0 and new_name!=original:
    		messages.success(request, 'Name Already Used!')
    		return render(request, 'myapp/modify_team.html',{'team_list':team_list})
    	else:
    		team_name=new_name
    		team_president=request.POST['team_president']
    		team_coach=request.POST['team_coach']
    		location=request.POST['location']
    		Team.objects.filter(team_name=original).update(team_name=new_name, team_president=team_president,team_coach=team_coach,location=location)
    		messages.success(request, 'Team Modified')
    		return render(request, 'myapp/modify_team.html',{'team_list':team_list})
    else:
    	return render(request, 'myapp/modify_team.html',{'team_list':team_list})

def add_player_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    return render(request, 'myapp/add_player_team.html')

def remove_player_team(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    return render(request, 'myapp/remove_player_team.html')

def back_main(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    return render(request, 'myapp/home_admin.html')

def team_section(request):
    try:
        if request.session['email'] != "admin@gmail.com":
            return render(request, 'myapp/login.html')
    except KeyError:
            return render(request, 'myapp/login.html')
    Teams_list= Team.objects.all()
    return render(request, 'myapp/team_section.html', {'Teams_list':Teams_list})
