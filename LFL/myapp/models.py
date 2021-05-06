from django.db import models

# Create your models here
class Team(models.Model):
    id = models.AutoField(primary_key=True)
    team_name = models.CharField( max_length = 50)
    team_president = models.CharField(max_length=50)
    team_coach = models.CharField(max_length=50)
    team_assistant_coach = models.CharField(max_length=50)
    team_players_number = models.IntegerField(default=0)
    location = models.CharField(max_length=50, default="unknown")
    team_logo = models.CharField(max_length=500, default="unknown")
    def _str_(self):
        return self.team_name

class Accounts(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(primary_key=True,max_length=30)
    password1 = models.CharField(max_length=30, default=0)
    password2 = models.CharField(max_length=30, default=0)
    favorite_team = models.ForeignKey(Team, on_delete=models.CASCADE, blank=True, null=True)

class Players(models.Model):
    player_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length = 50)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)
    position = models.CharField(max_length = 50)
    goals = models.IntegerField(default=0)
    assist = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class Game(models.Model):
    game_id = models.IntegerField(primary_key=True)
    team1_id = models.ForeignKey(Team,on_delete=models.CASCADE, related_name = '+')
    team2_id = models.ForeignKey(Team,on_delete=models.CASCADE, related_name = '+')
    game_date = models.DateTimeField()
    location = models.CharField(max_length= 75)
    team1_score = models.IntegerField(default=0)
    team2_score = models.IntegerField(default=0)
    ended = models.IntegerField(default=0)
    def __str__(self):
        return self.team1_id.team_name+" vs "+self.team2_id.team_name+ " on "+str(self.game_date)



class Event(models.Model):
    event_id = models.IntegerField(primary_key=True)
    event_type = models.CharField(max_length=50)
    event_date = models.DateTimeField()
    game_id = models.ForeignKey(Game,on_delete=models.CASCADE)
    player_id = models.ForeignKey(Players,on_delete=models.CASCADE)
    minute= models.IntegerField(default=0)
    def __str__(self):
        if(self.event_type=='yellow'):
            return self.player_id.name+ " - Yellow Card "
        elif (self.event_type=='red'):
            return self.player_id.name+ " - Red Card "
        elif (self.event_type=='Goal1'):
            return self.player_id.name+ " scored for "+self.game_id.team1_id.team_name
        elif (self.event_type=='Goal2'):
            return self.player_id.name+ " scored for "+self.game_id.team2_id.team_name

class StandingTable(models.Model):
    Team=models.ForeignKey(Team,primary_key=True,on_delete=models.CASCADE, related_name = '+')
    PointsAccumulated = models.IntegerField(default=0)
    Played= models.IntegerField(default=0)
    Win= models.IntegerField(default=0)
    Loss= models.IntegerField(default=0)
    Draw= models.IntegerField(default=0)
    Goals=models.IntegerField(default=0)
    Ranking=models.IntegerField(default=0)
