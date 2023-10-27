# Enter your Sleeper username and IFTTT Key below
# Set time_offset to 0 for ET, 1 for CT, 2 for MT, 3 for PT
# Set ir_notifcations to True to receive notifications for players in IR slots

user_name = 'enter_username'
IFTTT = 'enter_IFTTT_key'
time_offset = 1
ir_notifcations = False
prospect_alert_fantasy_points = 18
good_game_alert_fantasy_points = 25
huge_game_alert_fantasy_points = 40

import requests
import os
import json
import time
from datetime import datetime, date, timedelta
from dotenv import load_dotenv, find_dotenv

if user_name == 'enter_username':
    load_dotenv(find_dotenv())
    user_name = os.getenv('sleeper_username')
    IFTTT = os.getenv('IFTTT_key')
    

def ifttt(first, second, third):
    report = {}
    report["value1"] = first
    report["value2"] = second
    report["value3"] = third
    requests.post("https://maker.ifttt.com/trigger/sleeper_alert/with/key/"+IFTTT, data=report) 

today = date.today()
today_str = str(today)
yesterdaydate  = today - timedelta(days = 1)
yesterdayformat = yesterdaydate.strftime("%m/%d/%Y")

def is_file_older_than_x_days(file, days=7): 
    file_time = os.path.getmtime(file) 
    return ((time.time() - file_time) / 3600 > 24*days)

path = os.path.realpath(os.path.dirname(__file__))
os.chdir(path)
file = 'playercache.json'
isExist = os.path.exists(file)
if isExist == False or is_file_older_than_x_days(file) == True:
    data = requests.get("https://api.sleeper.app/v1/players/nba").json()
    json_object = json.dumps(data, indent=4)
    with open('playercache.json', "w") as f:
        f.write(json_object)

from nba_api.stats.static import players
from nba_api.stats.library.parameters import Season
from nba_api.stats.endpoints import leaguedashplayerstats

last3games = leaguedashplayerstats.LeagueDashPlayerStats(season=Season.current_season,last_n_games=3,per_mode_detailed='PerGame').get_normalized_json()
last3object = json.loads(last3games)
last3stats = last3object['LeagueDashPlayerStats']

yesterdaydata = leaguedashplayerstats.LeagueDashPlayerStats(season=Season.current_season,date_from_nullable=yesterdayformat,per_mode_detailed='PerGame').get_normalized_json()
yesterdayobject = json.loads(yesterdaydata)
yesterdaystats = yesterdayobject['LeagueDashPlayerStats']

gamesdata = requests.get("https://www.balldontlie.io/api/v1/games?start_date="+today_str+"&end_date="+today_str).json()
games = gamesdata['data']

seasonstatus = requests.get("https://api.sleeper.app/v1/state/nba").json()
season = seasonstatus['season']
week = str(seasonstatus['week'])

user = requests.get("https://api.sleeper.app/v1/user/"+user_name).json()
userid = user['user_id']
avatar = 'https://sleepercdn.com/avatars/'+user['avatar']

trendingdata = requests.get("https://api.sleeper.app/v1/players/nba/trending/add?lookback_hours=12&limit=100").json()

leagues = requests.get("https://api.sleeper.app/v1/user/"+userid+"/leagues/nba/"+season).json()

for league in leagues:
    leagueid = league['league_id']
    leaguename = league['name']
    scoring_settings = league['scoring_settings']
    pts_setting = scoring_settings['pts']
    ast_setting = scoring_settings['ast']
    reb_setting = scoring_settings['reb']
    stl_setting = scoring_settings['stl']
    blk_setting = scoring_settings['blk']
    to_setting = scoring_settings['to']
    dd_setting = scoring_settings['dd']
    td_setting = scoring_settings['td']

    leagueusers = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/users").json()

    leaguerosters = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/rosters").json()
    all_rostered = []
    for rosters in leaguerosters:
        owner_id = rosters['owner_id']
        if owner_id == userid:
            roster_id = rosters['roster_id']
            roster = rosters['players']
            starters = rosters['starters']
            ir = rosters['reserve']
            metadata = rosters['metadata']
            if ir_notifcations == True or ir is None:
                reserves = list(set(starters).symmetric_difference(set(roster)))
            else:
                reserves_ir = list(set(starters).symmetric_difference(set(roster)))
                reserves = list(set(ir).symmetric_difference(set(reserves_ir)))
        current_roster = rosters['players']
        for player in current_roster:
            all_rostered.append(player)

    prospects = []
    for player in trendingdata:
        if player['player_id'] not in all_rostered:
            prospects.append(player['player_id'])

    leaguematchups = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/matchups/"+week).json()
    for matchup in leaguematchups:
        if roster_id == matchup['roster_id']:
            matchup_id = matchup['matchup_id']
    for matchup in leaguematchups:
        if matchup_id == matchup['matchup_id'] and roster_id != matchup['roster_id']:
            opponent_roster = matchup['starters']
            opponent_roster_id = matchup['roster_id']
    for rosters in leaguerosters:
        if opponent_roster_id == rosters['roster_id']:
            opponent_user_id = rosters['owner_id']
    for users in leagueusers:
        if opponent_user_id == users['user_id']:
            opponent_team_name = users['display_name']

    os.chdir(path)
    f = open('playercache.json')
    data = json.load(f)
    player_names = []
    reserve_players = []
    for player in roster:
        if player != '0':
            player_name = []
            name = (data[player]['full_name'])
            player_name.append(name)
            player_name.append('myteam')
            player_nickname_key = 'p_nick_'+player
            if metadata != None:
                if player_nickname_key in metadata and metadata[player_nickname_key] != '':
                    nickname = metadata[player_nickname_key]
                    player_name.append(nickname)
            player_names.append(player_name)
    for player in reserves:
        if player != '0':
            reserve_player = []
            name = (data[player]['full_name'])
            team = (data[player]['team'])
            reserve_player.append(name)
            reserve_player.append(team)
            reserve_players.append(reserve_player)
    for player in opponent_roster:
        if player != '0':
            player_name = []
            name = (data[player]['full_name'])
            player_name.append(name)
            player_name.append('opponent')
            player_names.append(player_name)
    for player in prospects:
        player_name = []
        name = (data[player]['full_name'])
        player_name.append(name)
        player_name.append('prospect')
        player_names.append(player_name)
    print(player_names)
    for player in player_names:
        player_name = player[0]
        search = players.find_players_by_full_name(player_name)
        if search:
            id = search[0]['id']
            for log in yesterdaystats:
                if id == log['PLAYER_ID']:
                    pts = log['PTS'] * pts_setting
                    ast = log['AST'] * ast_setting
                    reb = log['REB'] * reb_setting
                    stl = log['STL'] * stl_setting
                    blk = log['BLK'] * blk_setting
                    to = log['TOV'] * to_setting
                    dd = log['DD2'] * dd_setting
                    td = log['TD3'] * td_setting
                    
                    fantasypoints = round(pts + ast + reb + stl + blk + to + dd + td, 1)

                    for log in last3stats:
                        if id == log['PLAYER_ID']:
                            gamesplayed = log['GP']
                            minutes = log['MIN']
                            pts_last3 = log['PTS'] * pts_setting
                            ast_last3 = log['AST'] * ast_setting
                            reb_last3 = log['REB'] * reb_setting
                            stl_last3 = log['STL'] * stl_setting
                            blk_last3 = log['BLK'] * blk_setting
                            to_last3 = log['TOV'] * to_setting
                            dd_last3 = log['DD2'] * dd_setting / gamesplayed
                            td_last3 = log['TD3'] * td_setting / gamesplayed                        

                            fplast3 = round(pts_last3 + ast_last3 + reb_last3 + stl_last3 + blk_last3 + to_last3 + dd_last3 + td_last3, 1)
                            
                            percentdiff = round((fantasypoints - fplast3) / fplast3 * 100, 1)
                            if percentdiff < 0:
                                change = 'lower'
                            else:
                                change = 'higher'

                            if (percentdiff > 20 and fantasypoints > good_game_alert_fantasy_points and player[1] != 'prospect') or (fantasypoints > huge_game_alert_fantasy_points) or (fplast3 > prospect_alert_fantasy_points and fantasypoints > prospect_alert_fantasy_points and minutes > 24 and player[1] == 'prospect'):
                                fantasypointsstr = str(fantasypoints)
                                percentdiffstr = str(percentdiff)
                                gamesplayedstr = str(gamesplayed)
                                fplast3str = str(fplast3)
                                minutestr = str(minutes)

                                if player[1] == 'myteam' and len(player) == 2:
                                    alert = f'Great game from {player_name} with {fantasypointsstr} points! {percentdiffstr}% {change} than his last {gamesplayedstr} game average of {fplast3str}.'
                                elif player[1] == 'myteam':
                                    alert = f'Great game from {player[2]} with {fantasypointsstr} points! {percentdiffstr}% {change} than his last {gamesplayedstr} game average of {fplast3str}.'
                                elif player[1] == 'opponent':
                                    alert = f"Oof! {player_name} on {opponent_team_name}'s team dropped {fantasypointsstr} points. {percentdiffstr}% {change} than his last {gamesplayedstr} game average of {fplast3str}."
                                elif player[1] == 'prospect':
                                    alert = f"{player_name} is trending and dropped {fantasypointsstr} points. {percentdiffstr}% {change} than his last {gamesplayedstr} game average of {fplast3str} playing {minutestr} MPG."
                                
                                print(alert)
                                ifttt(alert, leaguename, avatar)

                            else:
                                print(player_name+' done')

        else:
            print(player_name+' not found')


    for player in reserve_players:
        for game in games:
            if player[1] == game['home_team']['abbreviation'] or player[1] == game['visitor_team']['abbreviation']:
                gamestart_utc = game['status']
                stamp = datetime.strptime(gamestart_utc, '%Y-%m-%dT%H:%M:%SZ')
                final_time = stamp - timedelta(hours=time_offset+4)
                gamestart = final_time.strftime("%I:%M %p")
                if gamestart[0] == '0':
                    gamestartfinal = gamestart[1:]
                else:
                    gamestartfinal = gamestart
                
                alert = f'{player[0]} is on the bench and has a game today at {gamestartfinal}.'

                print(alert)
                ifttt(alert, leaguename, avatar)
