import requests
import json
import pandas as pd
import datetime
from statistics import mean

todaysGames = datetime.datetime.now().strftime("%m/%d/%Y")

def mlb_schedule():
    game_ids = []

    request = requests.get(f"http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={todaysGames}").text
    request_json = json.loads(request)
    games = (request_json['dates'][0]['games'])
    for game in games:
        game_ids.append(game['gamePk'])
    return game_ids

mlb_teamStats = []
mlb_advantages = []
teamAdvatage = []
projectedOutcome = []

for games in mlb_schedule():
    homeBA = []
    awayBA = []
    homeSLG = []
    awaySLG = []
    homeOBP = []
    awayOBP = []
    homeSO = []
    awaySO = []

    request = requests.get(f"https://statsapi.mlb.com/api/v1/schedule?gamePk={games}&language=en&hydrate=lineups").text
    games_request_json = json.loads(request)
    try:
        (games_request_json['dates'][0]['games'][0]['lineups']['homePlayers'])
    except:
        continue

    try:
        (games_request_json['dates'][0]['games'][0]['lineups']['awayPlayers'])
    except:
        continue

    homeTeamName = (games_request_json['dates'][0]['games'][0]['teams']['home']['team']['name'])
    awayTeamName = (games_request_json['dates'][0]['games'][0]['teams']['away']['team']['name'])
    homeTeam = (games_request_json['dates'][0]['games'][0]['lineups']['homePlayers'])
    awayTeam = (games_request_json['dates'][0]['games'][0]['lineups']['awayPlayers'])

    # Getting Batters Career Averages
    for player in homeTeam:
        try:
            id = (player['id'])
            request = requests.get(f"http://lookup-service-prod.mlb.com/json/named.sport_career_hitting.bam?league_list_id='mlb'&game_type='R'&player_id='{id}'").text
            request_json = json.loads(request)
            playerStats = (request_json['sport_career_hitting']['queryResults']['row'])
            homeBA.append(float(playerStats['avg']))
            homeSLG.append(float(playerStats['slg']))
            homeOBP.append(float(playerStats['obp']))
            homeSO.append(float(playerStats['so']) / float(playerStats['ab']))
        except:
            continue
    for player in awayTeam:
        try:
            id = (player['id'])
            request = requests.get(f"http://lookup-service-prod.mlb.com/json/named.sport_career_hitting.bam?league_list_id='mlb'&game_type='R'&player_id='{id}'").text
            request_json = json.loads(request)
            playerStats = (request_json['sport_career_hitting']['queryResults']['row'])
            awayBA.append(float(playerStats['avg']))
            awaySLG.append(float(playerStats['slg']))
            awayOBP.append(float(playerStats['obp']))
            awaySO.append(float(playerStats['so']) / float(playerStats['ab']))
        except:
            continue

    # Get Starting Pitcher Stats
    try:
        pitcherRequest = requests.get(f"http://statsapi.mlb.com/api/v1/game/{games}/boxscore").text
        pitcher_json = json.loads(pitcherRequest)

        homePitcher = pitcher_json['teams']['home']['pitchers'][0]
        awayPitcher = pitcher_json['teams']['away']['pitchers'][0]

        homePitcherRequest = requests.get(f"http://lookup-service-prod.mlb.com/json/named.sport_career_pitching.bam?league_list_id='mlb'&game_type='R'&player_id='{homePitcher}'").text
        homepitcherRequest_json = json.loads(homePitcherRequest)
        awayPitcherRequest = requests.get(f"http://lookup-service-prod.mlb.com/json/named.sport_career_pitching.bam?league_list_id='mlb'&game_type='R'&player_id='{awayPitcher}'").text
        awaypitcherRequest_json = json.loads(awayPitcherRequest)

        homePitcherStats = (homepitcherRequest_json['sport_career_pitching']['queryResults']['row'])
        awayPitcherStats = (awaypitcherRequest_json['sport_career_pitching']['queryResults']['row'])
    except:
        continue

    stats = {
        'Home Team': homeTeamName,
        "Away Team": awayTeamName,
        "Home Batting Average": round(mean(homeBA), 3),
        "Home Slugging %": round(mean(homeSLG), 3),
        "Home OBP %": round(mean(homeOBP), 3),
        "Home SO %": round(mean(homeSO), 2),
        "Home Starting ERA": round(float(homePitcherStats['era']), 2),
        "Home Starting WHIP": round(float(homePitcherStats['whip']), 2),
        "Home Starting OBP Against": round(float(homePitcherStats['obp']), 2),
        "Home Starting Homeruns/9 Against": round(float(homePitcherStats['h9']), 2),
        "Home Starting BB/9 Against": round(float(homePitcherStats['bb9']), 2),
        "Away Batting Average": round(mean(awayBA), 3),
        "Away Slugging %": round(mean(homeSLG), 3),
        "Away OBP %": round(mean(awayOBP), 3),
        "Away SO %": round(mean(awaySO), 2),
        "Away Starting ERA": round(float(awayPitcherStats['era']), 2),
        "Away Starting WHIP": round(float(awayPitcherStats['whip']), 2),
        "Away Starting OBP Against": round(float(awayPitcherStats['obp']), 2),
        "Away Starting Homeruns/9 Against": round(float(awayPitcherStats['h9']), 2),
        "Away Starting BB/9 Against": round(float(awayPitcherStats['bb9']), 2),
    }

    advantages = {
        'Home Team': homeTeamName,
        "Away Team": awayTeamName,
        "Home BA": round(mean(homeBA) - mean(awayBA), 3),
        "Home Slugging %": round(mean(homeSLG) - mean(awaySLG), 3),
        "Home OBP %": round(mean(homeOBP) - mean(awayOBP), 3),
        "Home SO %": round(mean(homeSO) - mean(awaySO), 3) * -1,
        "Home ERA": round(float(homePitcherStats['era']) - float(awayPitcherStats['era']), 3) * -1,
        "Home WHIP": round(float(homePitcherStats['whip']) - float(awayPitcherStats['whip']), 3) * -1,
        "Home OBP Against": (round(float(homePitcherStats['obp']), 2) - round(float(awayPitcherStats['obp']), 2)) * -1,
        "Home Homeruns/9 Against": (round(float(homePitcherStats['h9']), 2) - round(float(awayPitcherStats['h9']), 2)) * -1,
        "Home BB/9 Against": (round(float(homePitcherStats['bb9']), 2) - round(float(awayPitcherStats['bb9']),2)) * -1,
        "Away BA": round(mean(awayBA) - mean(homeBA), 3),
        "Away Slugging %": round(mean(awaySLG) - mean(homeSLG), 3),
        "Away OBP %": round(mean(awayOBP) - mean(homeOBP), 3),
        "Away SO %": round(mean(awaySO) - mean(homeSO), 3) * -1,
        "Away ERA": round(float(awayPitcherStats['era']) - float(homePitcherStats['era']), 3) * -1,
        "Away WHIP": round(float(awayPitcherStats['whip']) - float(homePitcherStats['whip']), 3) * -1,
        "Away OBP Against": (round(float(awayPitcherStats['obp']), 2) - round(float(homePitcherStats['obp']), 2)) * -1,
        "Away Homeruns/9 Against": (round(float(awayPitcherStats['h9']), 2) - round(float(homePitcherStats['h9']), 2)) * -1,
        "Away BB/9 Against": (round(float(awayPitcherStats['bb9']), 2) - round(float(homePitcherStats['bb9']), 2)) * -1,
    }

    homeAdvantage = advantages['Home SO %'] + advantages['Home Slugging %'] + advantages['Home ERA'] + advantages['Home Homeruns/9 Against'] + advantages['Home OBP Against']
    awayAdvantage = advantages['Away SO %'] + advantages['Away Slugging %'] + advantages['Away ERA'] + advantages['Away Homeruns/9 Against'] + advantages['Away OBP Against']

    # Get Game Info
    game_request = requests.get(f"http://statsapi.mlb.com/api/v1.1/game/{games}/feed/live").text
    game_info = json.loads(game_request)
    odds_date_formatted = datetime.datetime.now().strftime("%Y_%m_%d")
    game_odds_request = requests.get(f"https://www.fantasylabs.com/api/sportevents/3/{odds_date_formatted}").text
    game_odds_json = json.loads(game_odds_request)

    if game_info['gameData']['game']['doubleHeader'] == 'Y':
        continue

    for games in game_odds_json:
        if games['HomeTeam'] == homeTeamName:
            spread = (games['SpreadSummary'])
            ou = (games['OU'])
            first_pitch = games['EventTime']
            ml_away = games['MLVisitor']
            ml_home = games['MLHome']

    try:
        if (games_request_json['dates'][0]['games'][0]['teams']['home']['isWinner']) == True:
            homeWinner = 'Yes'
        elif (games_request_json['dates'][0]['games'][0]['teams']['home']['isWinner']) == False:
            homeWinner = 'No'
        else:
            homeWinner = 'TBD'
    except:
        homeWinner = 'TBD'

    try:
        if (games_request_json['dates'][0]['games'][0]['teams']['away']['isWinner']) == True:
            awayWinner = 'Yes'
        elif (games_request_json['dates'][0]['games'][0]['teams']['away']['isWinner']) == False:
            awayWinner = 'No'
        else:
            awayWinner = 'TBD'
    except:
        awayWinner = 'TBD'


    if advantages['Home Slugging %'] > advantages['Away Slugging %'] and advantages['Home OBP %'] > advantages['Away OBP %'] and advantages['Home ERA'] > advantages['Away ERA'] and advantages['Home WHIP'] > advantages['Away WHIP']:
        projectedWinner = {
            'Projected Winner': advantages['Home Team'],
            'Winner Advantage (Beta)': homeAdvantage,
            'Winner ML': ml_home,
            'Opponent': advantages['Away Team'],
            'Opponent Deficit': awayAdvantage,
            'Opponent ML': ml_away,
            'Spread': spread,
            'Over/Under': ou,
            'First Pitch': first_pitch,
            'Projected Winning Team Probable Pitcher': game_info['gameData']['probablePitchers']['home']['fullName'],
            'Opponent Teams Probable Pitcher': game_info['gameData']['probablePitchers']['away']['fullName'],
            'Winner': homeWinner,
            'Score': f"{advantages['Home Team']}: {games_request_json['dates'][0]['games'][0]['teams']['home']['score']}  {advantages['Away Team']}: {games_request_json['dates'][0]['games'][0]['teams']['away']['score']} ",
            'Weather': f"{game_info['gameData']['weather']['temp']}, {game_info['gameData']['weather']['condition']}"
        }
        projectedOutcome.append(projectedWinner)

    if advantages['Away Slugging %'] > advantages['Home Slugging %'] and advantages['Away OBP %'] > advantages['Home OBP %'] and advantages['Away ERA'] > advantages['Home ERA'] and advantages['Away WHIP'] > advantages['Home WHIP']:
        projectedWinner = {
            'Projected Winner': advantages['Away Team'],
            'Winner Advantage (Beta)': awayAdvantage,
            'Winner ML': ml_away,
            'Opponent': advantages['Home Team'],
            'Opponent Deficit': homeAdvantage,
            'Opponent ML': ml_home,
            'Spread': spread,
            'Over/Under': ou,
            'First Pitch': first_pitch,
            'Projected Winning Team Probable Pitcher': game_info['gameData']['probablePitchers']['away']['fullName'],
            'Opponent Teams Probable Pitcher': game_info['gameData']['probablePitchers']['home']['fullName'],
            'Winner': awayWinner,
            'Score': f"{advantages['Away Team']}: {games_request_json['dates'][0]['games'][0]['teams']['away']['score']}  {advantages['Home Team']}: {games_request_json['dates'][0]['games'][0]['teams']['home']['score']} ",
            'Weather': f"{game_info['gameData']['weather']['temp']}, {game_info['gameData']['weather']['condition']}"
        }

        projectedOutcome.append(projectedWinner)
    mlb_teamStats.append(stats)
    mlb_advantages.append(advantages)

projectedOutcome_dataframe = pd.DataFrame(data=projectedOutcome)
stats_dataframe = pd.DataFrame(data=mlb_teamStats)
advantages_dataframe = pd.DataFrame(data=mlb_advantages)
stats_dataframe_sorted = stats_dataframe.sort_values(by='Home Team')
advantages_dataframe_sorted = advantages_dataframe.sort_values(by='Home Team')

todaysDate = datetime.datetime.now().strftime("%A, %B %d, %Y")
updateTime = datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S")

htmlgameanalysis = """<h1>Game Analysis</h1>
<h3>Note: Once our Data shows a favorable matchup, the Game information will appear below</h3>
"""

# Setup HTML for Webpage
htmlheader = "<br></br> <h1> Team Advantages (Differences) </h1>"

htmlheader2 = "<h1>Team Statistics</h1>"


htmltop = f"""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="./MLBStyle.css">
<link href="style.css?t=[timestamp]" type="text/css" rel="stylesheet">
<div class="topnav">
  <a class="active" href="#home">Home</a>
</div>
</head>
<body>
<h1> Welcome to MLB Game Predictor</h1>
<h2> {todaysDate} </h2>
"""

htmlbottom = f"""
<br> </br>
<h4> Updated Time: {updateTime} </h4>
</body>
</html>
"""

# Export Tables to HTML Page
with open('/var/www/html/index.html', 'w') as _file:
    _file.write(htmltop + htmlgameanalysis + projectedOutcome_dataframe.to_html(index=False) + htmlheader + advantages_dataframe_sorted.to_html(index=False) + htmlheader2 + stats_dataframe_sorted.to_html(index=False) + htmlbottom)
