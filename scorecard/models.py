from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import datetime
from simple_history.models import HistoricalRecords
# Create your models here.

class Team(models.Model):
    team_name = models.CharField(max_length=30)
    played = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    def __str__(self):
        return self.team_name

class Match(models.Model):
    match_id = models.CharField(max_length=30)
    created_on = models.DateTimeField(default=datetime.now)
    team1 = models.ForeignKey(Team, related_name='team1_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_matches', on_delete=models.CASCADE)
    t1run1 = models.IntegerField(default=0)
    t1run2 = models.IntegerField(default=0)
    t2run1 = models.IntegerField(default=0)
    t2run2 = models.IntegerField(default=0)
    t1wkt1 = models.IntegerField(default=0)
    t1wkt2 = models.IntegerField(default=0)
    t2wkt1 = models.IntegerField(default=0)
    t2wkt2 = models.IntegerField(default=0)
    t1overs1 = models.DecimalField(default=0.0, max_digits=4, decimal_places=1)
    t1overs2 = models.DecimalField(default=0.0, max_digits=4, decimal_places=1)
    t2overs1 = models.DecimalField(default=0.0, max_digits=4, decimal_places=1)
    t2overs2 = models.DecimalField(default=0.0, max_digits=4, decimal_places=1)
    batting = models.ForeignKey(Team, related_name='batting_matches', on_delete=models.CASCADE,null=True,blank=True)
    bowler = models.ForeignKey(User, related_name='bowling_matches', on_delete=models.CASCADE,null=True,blank=True)
    striker = models.ForeignKey(User, related_name='striker_matches', on_delete=models.CASCADE,null=True,blank=True)
    non_striker = models.ForeignKey(User, related_name='non_striker_matches', on_delete=models.CASCADE,null=True,blank=True)
    innings = models.IntegerField(
    default=1,
    validators=[
        MaxValueValidator(2),
        MinValueValidator(1)
    ]
    )
    won = models.ForeignKey(Team, related_name='won', on_delete=models.CASCADE,null=True,blank=True)
    ball_record = models.JSONField(default=list)
    history = HistoricalRecords()
    def __str__(self):
        return f"Match {self.match_id}"

class Players(models.Model):
    name = models.ForeignKey(User, related_name="User", on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='players', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='players', on_delete=models.CASCADE)
    runs1 = models.IntegerField(default=0)
    runs2 = models.IntegerField(default=0)
    balls1 = models.IntegerField(default=0)
    balls2 = models.IntegerField(default=0)
    overs1 = models.IntegerField(default=0)
    overs2 = models.IntegerField(default=0)
    wkt1 = models.IntegerField(default=0)
    wkt2 = models.IntegerField(default=0)
    bruns1 = models.IntegerField(default=0)
    bruns2 = models.IntegerField(default=0)
    out1 = models.BooleanField(default=False)
    out2 = models.BooleanField(default=False)
    sixes = models.IntegerField(default=0,null=True, blank=True)
    fours = models.IntegerField(default=0,null=True, blank=True)
    catches = models.IntegerField(default=0,null=True, blank=True)
    history = HistoricalRecords()
    def __str__(self):
        return f"Player {self.name.username} in Match {self.match.match_id}"

class Wicket(models.Model):
    match = models.ForeignKey(Match, related_name='wickets', on_delete=models.CASCADE)
    player = models.ForeignKey(Players, related_name='wickets', on_delete=models.CASCADE)
    bowler = models.ForeignKey(User, related_name='bowled_wickets', on_delete=models.CASCADE)
    caught_by = models.ForeignKey(User, related_name='caught_wickets', on_delete=models.CASCADE, null=True, blank=True)
    run_out_by = models.ForeignKey(User, related_name='run_out_wickets', on_delete=models.CASCADE, null=True, blank=True)
    history = HistoricalRecords()
    def __str__(self):
        return f"Wicket by {self.bowler.username} in Match {self.match.match_id}"
