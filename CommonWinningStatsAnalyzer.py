# Author
    # Brian Schroeder

# Synopsis
    # This program gets the winner for each game and outputs the stats they were leading in.
    # The Output will be the total number of times that category was higher for the winning team vs the losing

import requests
import json
from collections import Counter
import pandas as pd

batting_winningStats = []
pitching_winningStats = []
categories = 'batting', 'pitching'

def mlb_games(*gamedates):
    for gamedate in gamedates:
        request = requests.get(f"http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={gamedate}").text
        request_json = json.loads(request)
        games = (request_json['dates'][0]['games'])

        for game in games:

            for category in categories:

                request = requests.get(f"http://statsapi.mlb.com{(game['link'])}").text
                request_json = json.loads(request)
                awayStats = (request_json['liveData']['boxscore']['teams']['away']['teamStats'][category])
                homeStats = (request_json['liveData']['boxscore']['teams']['home']['teamStats'][category])

                try:
                    if (game['teams']['home']['isWinner']) == True:
                        for key in homeStats.keys():
                            if homeStats[key] > awayStats[key]:
                                if category == 'batting':
                                    batting_winningStats.append(key)
                                if category == 'pitching':
                                    pitching_winningStats.append(key)
                    else:
                        for key in homeStats.keys():
                            if homeStats[key] < awayStats[key]:
                                if category == 'batting':
                                    batting_winningStats.append(key)
                                if category == 'pitching':
                                    pitching_winningStats.append(key)

                except:
                    continue

mlb_games('04/01/2021', '04/02/2021','04/03/2021','04/04/2021')

common_batting_winning_stats = (dict(Counter(batting_winningStats)))
common_pitching_winning_stats = (dict(Counter(pitching_winningStats)))
sorted_common_batting_winning_stats = (sorted(common_batting_winning_stats.items(), key=lambda x: x[1], reverse=True))
sorted_common_pitching_winning_stats = (sorted(common_pitching_winning_stats.items(), key=lambda x: x[1], reverse=True))

batting_stats_dataframe = pd.DataFrame(data=sorted_common_batting_winning_stats)
pitching_stats_dataframe = pd.DataFrame(data=sorted_common_pitching_winning_stats)

print('\n\nCommon Winning Leading Batting Categories\n\n')
print(batting_stats_dataframe)

print('\n\nCommon Winning Leading Pitching Categories\n\n')
print(pitching_stats_dataframe)
