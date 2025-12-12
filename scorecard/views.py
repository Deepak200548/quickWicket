from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from django.contrib.auth.models import User
import datetime
import random
import string
from .models import Team,Match,Players
from django.http import JsonResponse
import json
from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/create_game')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password.'})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect("/")

def players_list(request):
    players = User.objects.filter()
    return render(request,"players.html",{"players":players})

def player_profile(request,username):
    player_user = get_object_or_404(User, username=username)
    
    # Fetch all Player objects for this user
    player_stats = Players.objects.filter(name=player_user).select_related('team', 'match')
    total_inings = 0
    for player in player_stats:
        if player.out1== True:
            total_inings+=1
        if player.out2== True:
            total_inings+=1
    # Total stats
    total_runs = sum(player.runs1 + player.runs2 for player in player_stats)
    total_balls = sum(player.balls1 + player.balls2 for player in player_stats)
    total_wickets = sum(player.wkt1 + player.wkt2 for player in player_stats)
    total_overs = sum(player.overs1 + player.overs2 for player in player_stats)
    total_bowling_runs = sum(player.bruns1 + player.bruns2 for player in player_stats)
    matches_played = player_stats.count()

    # Calculated stats
    average_strike_rate = (total_runs / total_balls * 100) if total_balls > 0 else 0
    average_economy = (total_bowling_runs / (total_overs/6)) if total_overs > 0 else 0
    average_wickets = (total_wickets / matches_played) if matches_played > 0 else 0
    batting_average = (total_runs / (total_inings)) if total_inings > 0 else total_runs
    
    context = {
        'player_user': player_user,
        'player_stats': player_stats,
        'total_runs': total_runs,
        'total_balls': total_balls,
        'total_overs': total_overs/6,
        'total_wickets': total_wickets,
        'total_bowling_runs': total_bowling_runs,
        'matches_played': matches_played,
        'average_strike_rate': round(average_strike_rate, 2),
        'average_economy': round(average_economy, 2),
        'average_wickets': round(average_wickets, 2),
        'batting_average': round(batting_average, 2),
    }
    return render(request, 'player_profile.html', context)

def matches(request):
    matches = Match.objects.filter()
    return render(request,"matches.html",{"matches":matches})

def serialize_player(player):
    return {
        "id": player.id,
        "username": player.name.username,
        "email": player.name.email,
        "first_name": player.name.first_name,
        "last_name": player.name.last_name,
        "runs1": player.runs1,
        "runs2": player.runs2,
        "balls1": player.balls1,
        "balls2": player.balls2,
        "overs1": player.overs1,
        "overs2": player.overs2,
        "wkt1": player.wkt1,
        "wkt2": player.wkt2,
        "bruns1": player.bruns1,
        "bruns2": player.bruns2,
        "out1": player.out1,
        "out2": player.out2,
        "team": player.team.team_name,
    }

def game_details_json(request, game_id):
    match = get_object_or_404(Match, match_id=game_id)

    players1 = Players.objects.filter(match=match, team=match.team1)
    players2 = Players.objects.filter(match=match, team=match.team2)

    bowler = Players.objects.filter(match=match, name=match.bowler).first() if match.bowler else None
    striker = Players.objects.filter(match=match, name=match.striker).first() if match.striker else None
    non_striker = Players.objects.filter(match=match, name=match.non_striker).first() if match.non_striker else None

    cont = {
        "match_id": str(match.match_id),
        "team_1": str(match.team1.team_name) if match.team1 else "",
        "team_2": str(match.team2.team_name) if match.team2 else "",
        "t1run1": match.t1run1,
        "t1run2": match.t1run2,
        "t2run1": match.t2run1,
        "t2run2": match.t2run2,
        "t1wkt1": match.t1wkt1,
        "t1wkt2": match.t1wkt2,
        "t2wkt1": match.t2wkt1,
        "t2wkt2": match.t2wkt2,
        "t1overs1": match.t1overs1,
        "t1overs2": match.t1overs2,
        "t2overs1": match.t2overs1,
        "t2overs2": match.t2overs2,
        "batting": str(match.batting.team_name) if match.batting else "",
        "bowler": serialize_player(bowler) if bowler else None,
        "striker": serialize_player(striker) if striker else None,
        "non_striker": serialize_player(non_striker) if non_striker else None,
        "innings": match.innings,
        "won": str(match.won.team_name) if match.won else "",
        "t1_players": [serialize_player(p) for p in players1],
        "t2_players": [serialize_player(p) for p in players2],
        "ball_record": match.ball_record,
    }

    return JsonResponse(cont, safe=False)

def game(request, game_id):
    match = Match.objects.get(match_id=game_id)
    players1 = Players.objects.filter(match=match,team=match.team1)
    players2 = Players.objects.filter(match=match,team=match.team2)
    cont = {
    "match_id": str(match.match_id),
    "team_1": str(match.team1.team_name) if match.team1 else "",
    "team_2": str(match.team2.team_name) if match.team2 else "",
    "t1run1": match.t1run1,
    "t1run2": match.t1run2,
    "t2run1": match.t2run1,
    "t2run2": match.t2run2,
    "t1wkt1": match.t1wkt1,
    "t1wkt2": match.t1wkt2,
    "t2wkt1": match.t2wkt1,
    "t2wkt2": match.t2wkt2,
    "t1overs1": match.t1overs1,
    "t1overs2": match.t1overs2,
    "t2overs1": match.t2overs1,
    "t2overs2": match.t2overs2,
    "batting": str(match.batting.team_name) if match.batting else "",
    "bowler": Players.objects.get(match=match,name=match.bowler) if match.bowler else "",
    "striker": Players.objects.get(match=match,name=match.striker) if match.striker else "",
    "non_striker": Players.objects.get(match=match,name=match.non_striker) if match.non_striker else "",
    "innings": match.innings,
    "won":str(match.won.team_name) if match.won else "",
    "t1_players":players1,
    "t2_players":players2,
    "ball_record": match.ball_record,
    }

    if str(request.user) == "AnonymousUser":
        return render(request, 'game_disp.html')
    else:
        return render(request,"game.html",cont)


def create_game(request):
    if str(request.user) != "AnonymousUser":
        players = User.objects.values_list('username', flat=True)
        teams = Team.objects.values_list('team_name',flat=True)
        return render(request, 'create_game.html', {"players": players,"teams":teams})
    return redirect("login")

def begin_game(request):
    if request.method == "POST":
            try:
                data = json.loads(request.body)
                team1 = data.get("team1", [])
                team2 = data.get("team2", [])
                toss_winner = data.get("toss_winner","").strip()
                team1Name = data.get("team1name")
                team2Name = data.get("team2name")
                now = datetime.datetime.now()
                ist_offset = datetime.timedelta(hours=5, minutes=30)
                ist_now = now + ist_offset
                timestamp = ist_now.strftime("%Y%m%d_%H%M%S")
                random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                room_id = f"{timestamp}_{random_string}"
                new_match = Match.objects.create(
                    match_id=room_id,  # Replace with your unique match ID logic
                    team1=Team.objects.get(team_name=team1Name),
                    team2=Team.objects.get(team_name=team2Name),
                    batting = Team.objects.get(team_name=toss_winner)
                )
                for p1 in team1:
                    Players.objects.create(
                        name=User.objects.get(username=p1),
                        match=new_match,
                        team=Team.objects.get(team_name=team1Name)
                    )
                for p2 in team2:
                    Players.objects.create(
                        name=User.objects.get(username=p2),
                        match=new_match,
                        team=Team.objects.get(team_name=team2Name)
                    )   
                return JsonResponse({"message": "Game created successfully!", "room_id":room_id})

            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data."}, status=400)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error":"Empty request"},code=500)


def game_update(request):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")
        match_id = data.get("match_id")
        match = Match.objects.get(match_id=match_id)
        change_bowler = "NO"
        if action == "updateScore":
            runs = int(data.get("runs", 0))
            striker = Players.objects.get(match=match, name=match.striker)
            bowler = Players.objects.get(match=match, name=match.bowler)
            match.ball_record.append(str(runs))
            if match.innings == 1 and match.batting == match.team1:
                match.t1run1 += runs
                if match.t1overs1 - int(match.t1overs1) == Decimal('0.5'):
                    match.t1overs1 = Decimal(int(match.t1overs1)) + Decimal('1.0')
                    bowler.overs1 = int(bowler.overs1) + 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                striker.runs1 += runs
                striker.balls1 += 1
                bowler.bruns1 += runs
                if match.t1overs1 == Decimal('10.0'):
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    match.batting = match.team2
                    if match.t2overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.innings == 1 and match.batting == match.team2:
                match.t2run1 += runs
                if match.t2overs1 - int(match.t2overs1) == Decimal('0.5'):
                    match.t2overs1 = Decimal(int(match.t2overs1)) + Decimal('1.0')
                    bowler.overs1 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                striker.runs1 += runs
                striker.balls1 += 1
                bowler.bruns1 += runs
                if match.t2overs1 == Decimal('10.0'):
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    match.batting = match.team1
                    if match.t1overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.innings == 2 and match.batting == match.team2:
                match.t2run2 += runs
                if match.t2overs2 - int(match.t2overs2) == Decimal('0.5'):
                    match.t2overs2 = Decimal(int(match.t2overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                striker.runs2 += runs
                striker.balls2 += 1
                bowler.bruns2 += runs
                if match.t2overs2 == Decimal('10.0'):
                    if match.t1overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None
                        match.batting = match.team1

            elif match.innings == 2 and match.batting == match.team1:
                match.t1run2 += runs
                if match.t1overs2 - int(match.t1overs2) == Decimal('0.5'):
                    match.t1overs2 = Decimal(int(match.t1overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                striker.runs2 += runs
                striker.balls2 += 1
                bowler.bruns2 += runs
                if match.t1overs2 == Decimal('10.0'):
                    if match.t2overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None
                        match.batting = match.team2

            match.save()
            striker.save()
            bowler.save()
            return JsonResponse({"message": "OK", "Change_bowler": change_bowler}, status=200)
        if action == 'updateWkt':
            bowler = Players.objects.get(match=match, name=match.bowler)
            batter = Players.objects.get(match=match, name=match.striker)
            match.ball_record.append("W")
            if match.batting == match.team1 and match.innings == 1:
                match.t1wkt1 += 1
                bowler.wkt1 += 1
                if match.t1overs1 - int(match.t1overs1) == Decimal('0.5'):
                    match.t1overs1 = Decimal(int(match.t1overs1)) + Decimal('1.0')
                    bowler.overs1 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                batter.balls1 += 1
                batter.out1 = True
                match.striker = None
                batter.save()
                bowler.save()
                team1p = Players.objects.filter(match=match, team=match.team1, out1=False)
                print(team1p)
                if team1p.count() == 0 or match.t1overs1 == Decimal('10.0'):
                    match.batting = match.team2
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    if match.t2overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.batting == match.team1 and match.innings == 2:
                match.t1wkt2 += 1
                bowler.wkt2 += 1
                if match.t1overs2 - int(match.t1overs2) == Decimal('0.5'):
                    match.t1overs2 = Decimal(int(match.t1overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                batter.balls2 += 1
                batter.out2 = True
                match.striker = None
                batter.save()
                bowler.save()
                team1p = Players.objects.filter(match=match, team=match.team1, out2=False)
                if team1p.count() == 0 or match.t1overs2 == Decimal('10.0'):
                    if match.t2overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.batting = match.team2
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None

            elif match.batting == match.team2 and match.innings == 1:
                match.t2wkt1 += 1
                bowler.wkt1 += 1
                if match.t2overs1 - int(match.t2overs1) == Decimal('0.5'):
                    match.t2overs1 = Decimal(int(match.t2overs1)) + Decimal('1.0')
                    bowler.overs1 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                batter.balls1 += 1
                batter.out1 = True
                match.striker = None
                batter.save()
                bowler.save()
                team2p = Players.objects.filter(match=match, team=match.team2, out1=False)
                if team2p.count() == 0 or match.t2overs1 == Decimal('10.0'):
                    match.batting = match.team1
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    if match.t1overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.batting == match.team2 and match.innings == 2:
                match.t2wkt2 += 1
                bowler.wkt2 += 1
                if match.t2overs2 - int(match.t2overs2) == Decimal('0.5'):
                    match.t2overs2 = Decimal(int(match.t2overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                batter.balls2 += 1
                batter.out2 = True
                match.striker = None
                batter.save()
                bowler.save()
                team2p = Players.objects.filter(match=match, team=match.team2, out2=False)
                if team2p.count() == 0 or match.t2overs2 == Decimal('10.0'):
                    match.bowler = None
                    match.ball_record = []
                    if match.t1overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None
                        match.batting = match.team1

            match.save()
            return JsonResponse({"message": "OK", "Change_bowler": change_bowler}, status=200)
        if action == "updateWide":
            match.ball_record.append("Wd")
            if match.batting == match.team1 and match.innings == 1:
                match.t1run1 += 1
                bowler = Players.objects.get(match=match, name=match.bowler)
                bowler.bruns1 += 1

            elif match.batting == match.team1 and match.innings == 2:
                match.t1run2 += 1
                bowler = Players.objects.get(match=match, name=match.bowler)
                bowler.bruns2 += 1

            elif match.batting == match.team2 and match.innings == 1:
                match.t2run1 += 1
                bowler = Players.objects.get(match=match, name=match.bowler)
                bowler.bruns1 += 1

            elif match.batting == match.team2 and match.innings == 2:
                match.t2run2 += 1
                bowler = Players.objects.get(match=match, name=match.bowler)
                bowler.bruns2 += 1
            match.save()
            bowler.save()
            return JsonResponse({"message": "OK", "Change_bowler": "No"}, status=200)
        if action == "updateNB":
            match.ball_record.append("Nb")
            runs = int(data.get("runs", 0)) 
            if match.batting == match.team1 and match.innings == 1:
                match.t1run1 += runs + 1 
                striker = Players.objects.get(match=match, name=match.striker)
                bowler = Players.objects.get(match=match, name=match.bowler)
                striker.runs1 += runs
                striker.balls1 +=1
                bowler.bruns1 += runs + 1  

            elif match.batting == match.team1 and match.innings == 2:
                match.t1run2 += runs + 1
                striker = Players.objects.get(match=match, name=match.striker)
                bowler = Players.objects.get(match=match, name=match.bowler)
                striker.runs2 += runs
                striker.balls2 +=1
                bowler.bruns2 += runs + 1

            elif match.batting == match.team2 and match.innings == 1:
                match.t2run1 += runs + 1
                striker = Players.objects.get(match=match, name=match.striker)
                bowler = Players.objects.get(match=match, name=match.bowler)
                striker.runs1 += runs
                striker.balls1 +=1
                bowler.bruns1 += runs + 1

            elif match.batting == match.team2 and match.innings == 2:
                match.t2run2 += runs + 1
                striker = Players.objects.get(match=match, name=match.striker)
                bowler = Players.objects.get(match=match, name=match.bowler)
                striker.runs2 += runs
                striker.balls2 +=1
                bowler.bruns2 += runs + 1

            match.save()
            striker.save()
            bowler.save()

            return JsonResponse({"message": "OK"}, status=200)
        if action == "changeStrike":
            temp = match.striker
            match.striker = match.non_striker
            match.non_striker = temp
            match.save()
            return JsonResponse({"message": "OK"}, status=200)
        if action == "strike":
            new_striker = data.get("new_striker")
            match.striker = User.objects.get(username=new_striker)
            match.save()
            return JsonResponse({"message":"Ok"},status=200)
        if action == "non-strike":
            new_striker = data.get("new_striker")
            match.non_striker = User.objects.get(username=new_striker)
            match.save()
            return JsonResponse({"message":"Ok"},status=200)
        if action == "changeBowler":
            new_bowler = data.get("new_bowler")
            match.bowler = User.objects.get(username=new_bowler)
            match.save()
            return JsonResponse({"message":"Ok"},status=200)
        if action == "followon":
            if match.innings == 2:
                if match.batting.team_name == match.team1.team_name:
                    match.batting = match.team2
                else:
                    match.batting = match.team1
                match.save()
                return JsonResponse({"message":"OK"},status=200)
            else:
                return JsonResponse({"message":"Cannot follow on in first innings"},status=400)
        if action == 'runout':
            match.ball_record.append("RO")
            bowler = Players.objects.get(match=match, name=match.bowler)
            batter = Players.objects.get(match=match, name=match.striker)
            if match.non_striker != None:
                nbatter = Players.objects.get(match=match, name=match.non_striker)
            else:
                nbatter = None
            rruns = int(data.get("runs", 0))
            slowB = data.get("slowB")
            if match.batting == match.team1 and match.innings == 1:
                match.t1wkt1 += 1
                match.t1run1 += rruns
                if match.t1overs1 - int(match.t1overs1) == Decimal('0.5'):
                    match.t1overs1 = Decimal(int(match.t1overs1)) + Decimal('1.0')
                    bowler.overs1 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                batter.runs1 += rruns
                batter.balls1 += 1
                if slowB == "striker":
                    batter.out1 = True
                    match.striker = None
                else:
                    nbatter.out1 = True
                    match.non_striker = None
                batter.save()
                bowler.save()
                if nbatter != None:
                    nbatter.save()
                team1p = Players.objects.filter(match=match, team=match.team1, out1=False)
                print(team1p)
                if team1p.count() == 0 or match.t1overs1 == Decimal('10.0'):
                    match.batting = match.team2
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    if match.t2overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.batting == match.team1 and match.innings == 2:
                match.t1wkt2 += 1
                match.t1run2 += rruns
                if match.t1overs2 - int(match.t1overs2) == Decimal('0.5'):
                    match.t1overs2 = Decimal(int(match.t1overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t1overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                batter.runs2 += rruns
                batter.balls2 += 1
                if slowB == "striker":
                    batter.out2 = True
                    match.striker = None
                else:
                    nbatter.out2 = True
                    match.non_striker = None
                batter.save()
                bowler.save()
                if nbatter != None:
                    nbatter.save()
                team1p = Players.objects.filter(match=match, team=match.team1, out2=False)
                if team1p.count() == 0 or match.t1overs2 == Decimal('10.0'):
                    if match.t2overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.batting = match.team2
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None

            elif match.batting == match.team2 and match.innings == 1:
                match.t2wkt1 += 1
                match.t2run1 += rruns
                if match.t2overs1 - int(match.t2overs1) == Decimal('0.5'):
                    match.t2overs1 = Decimal(int(match.t2overs1)) + Decimal('1.0')
                    bowler.overs1 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs1 += Decimal('0.1')
                    bowler.overs1 += 1
                batter.runs1 += rruns
                batter.balls1 += 1
                if slowB == "striker":
                    batter.out1 = True
                    match.striker = None
                else:
                    nbatter.out1 = True
                    match.non_striker = None
                batter.save()
                bowler.save()
                if nbatter != None:
                    nbatter.save()
                team2p = Players.objects.filter(match=match, team=match.team2, out1=False)
                if team2p.count() == 0 or match.t2overs1 == Decimal('10.0'):
                    match.batting = match.team1
                    match.bowler = None
                    match.ball_record = []
                    match.striker = None
                    match.non_striker = None
                    if match.t1overs1 != Decimal('0.0'):
                        match.innings = 2

            elif match.batting == match.team2 and match.innings == 2:
                match.t2wkt2 += 1
                match.t2run2 += rruns
                if match.t2overs2 - int(match.t2overs2) == Decimal('0.5'):
                    match.t2overs2 = Decimal(int(match.t2overs2)) + Decimal('1.0')
                    bowler.overs2 += 1
                    change_bowler = "YES"
                    match.bowler = None
                    match.ball_record = []
                else:
                    match.t2overs2 += Decimal('0.1')
                    bowler.overs2 += 1
                batter.runs2 += rruns
                batter.balls2 += 1
                if slowB == "striker":
                    batter.out2 = True
                    match.striker = None
                else:
                    nbatter.out2 = True
                    match.non_striker = None
                batter.save()
                bowler.save()
                if nbatter != None:
                    nbatter.save()
                team2p = Players.objects.filter(match=match, team=match.team2, out2=False)
                if team2p.count() == 0 or match.t2overs2 == Decimal('10.0'):
                    match.bowler = None
                    match.ball_record = []
                    if match.t1overs2 != Decimal('0.0'):
                        if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                            match.won = match.team2
                        else:
                            match.won = match.team1
                    else:
                        match.bowler = None
                        match.ball_record = []
                        match.striker = None
                        match.non_striker = None
                        match.batting = match.team1

            match.save()
            return JsonResponse({"message": "OK", "Change_bowler": change_bowler}, status=200)
        if match.t2overs2 != Decimal('0.0') and match.t1overs2 != Decimal('0.0'):
            if (match.t1run1 + match.t1run2) < (match.t2run1 + match.t2run2):
                match.won = match.team2
            else:
                match.won = match.team1
            match.save()
        
    return JsonResponse({"message": "Something went wrong"}, status=500)

def undo_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        match_ids = data.get('match_id')

        match = Match.objects.get(match_id=str(match_ids))
        Playerss = Players.objects.filter(match=match)
        last_history = match.history.latest('history_date')
        # Revert to the previous state
        previous_state = match.history.as_of(last_history.history_date - datetime.timedelta(seconds=1))
        match.t1run1 = previous_state.t1run1
        match.t1run2 = previous_state.t1run2
        match.t2run1 = previous_state.t2run1
        match.t2run2 = previous_state.t2run2
        match.t1wkt1 = previous_state.t1wkt1
        match.t1wkt2 = previous_state.t1wkt2
        match.t2wkt1 = previous_state.t2wkt1
        match.t2wkt2 = previous_state.t2wkt2
        match.t1overs1 = previous_state.t1overs1
        match.t1overs2 = previous_state.t1overs2
        match.t2overs1 = previous_state.t2overs1
        match.t2overs2 = previous_state.t2overs2
        match.batting = previous_state.batting
        match.bowler = previous_state.bowler
        match.striker = previous_state.striker
        match.non_striker = previous_state.non_striker
        match.innings = previous_state.innings
        match.ball_record = previous_state.ball_record
        # Update other fields as needed...
        match.save()
        for player in Playerss:
            player_runs = player.history.as_of(last_history.history_date - datetime.timedelta(seconds=1))
            player.runs1 = player_runs.runs1
            player.runs2 = player_runs.runs2
            player.balls1 = player_runs.balls1
            player.balls2 = player_runs.balls2
            player.overs1 = player_runs.overs1
            player.overs2 = player_runs.overs2
            player.wkt1 = player_runs.wkt1
            player.wkt2 = player_runs.wkt2
            player.bruns1 = player_runs.bruns1
            player.bruns2 = player_runs.bruns2
            player.out1 = player_runs.out1
            player.out2 = player_runs.out2
            player.save()
        return JsonResponse({'status': 'success', 'message': 'Last action undone.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

