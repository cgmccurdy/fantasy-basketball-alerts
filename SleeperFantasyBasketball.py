# Enter your Sleeper username, Discord webhook URL, and Ball Don't Lie API key below
# Set time_offset to 0 for ET, 1 for CT, 2 for MT, 3 for PT
# Set ir_notifcations to True to receive notifications for players in IR slots

user_name = 'enter_username'
webhook_url = 'enter_webhook_url'
balldontlie_api_key = 'enter_api_key'
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
    webhook_url = os.getenv('discord_webhook_url')
    balldontlie_api_key = os.getenv('ball_dont_lie_api')

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

gamesdata = requests.get("https://api.balldontlie.io/v1/games?start_date="+today_str+"&end_date="+today_str, headers={"Authorization": balldontlie_api_key}).json()
games = gamesdata['data']

seasonstatus = requests.get("https://api.sleeper.app/v1/state/nba").json()
season = seasonstatus['season']
week = str(seasonstatus['week'])

user = requests.get("https://api.sleeper.app/v1/user/"+user_name).json()
userid = user['user_id']
user_avatar = 'https://sleepercdn.com/avatars/'+user['avatar']

trendingdata = requests.get("https://api.sleeper.app/v1/players/nba/trending/add?lookback_hours=12&limit=100").json()

leagues = requests.get("https://api.sleeper.app/v1/user/"+userid+"/leagues/nba/"+season).json()

for league in leagues:
    leagueid = league['league_id']
    leaguename = league['name']
    league_avatar = 'https://sleepercdn.com/avatars/'+league['avatar']
    scoring_settings = league['scoring_settings']
    try:
        pts_setting = scoring_settings['pts']
    except:
        pts_setting = 0
    try:
        ast_setting = scoring_settings['ast']
    except:
        ast_setting = 0
    try:
        reb_setting = scoring_settings['reb']
    except:
        reb_setting = 0
    try:
        stl_setting = scoring_settings['stl']
    except:
        stl_setting = 0
    try:
        blk_setting = scoring_settings['blk']
    except:
        blk_setting = 0
    try:
        to_setting = scoring_settings['to']
    except:
        to_setting = 0
    try:
        fgm_setting = scoring_settings['fgm']
    except:
        fgm_setting = 0
    try:
        fgmi_setting = scoring_settings['fgmi']
    except:
        fgmi_setting = 0
    try:
        ftm_setting = scoring_settings['ftm']
    except:
        ftm_setting = 0
    try:
        ftmi_setting = scoring_settings['ftmi']
    except:
        ftmi_setting = 0
    try:
        threes_setting = scoring_settings['tpm']
    except:
        threes_setting = 0
    try:
        dd_setting = scoring_settings['dd']
    except:
        dd_setting = 0
    try:
        td_setting = scoring_settings['td']
    except:
        td_setting = 0
    try:
        tech_setting = scoring_settings['tf']
    except:
        tech_setting = 0
    try:
        flagrant_setting = scoring_settings['ff']
    except:
        flagrant_setting = 0
    try:
        bonus_pts40_setting = scoring_settings['bonus_pt_40p']
    except:
        bonus_pts40_setting = 0
    try:
        bonus_pts50_setting = scoring_settings['bonus_pt_50p']
    except:
        bonus_pts50_setting = 0
    try:
        bonus_reb20_setting = scoring_settings['bonus_reb_20p']
    except:
        bonus_reb20_setting = 0
    try:
        bonus_ast15_setting = scoring_settings['bonus_ast_15p']
    except:
        bonus_ast15_setting = 0

    leagueusers = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/users").json()
    print(leagueusers)

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

    trending = []
    for player in trendingdata:
        if player['player_id'] not in all_rostered:
            trending.append(player['player_id'])

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
    for user in leagueusers:
        if userid == user['user_id']:
            try:
                team_name = user['metadata']['team_name']
            except:
                team_name = user['display_name']
        if opponent_user_id == user['user_id']:
            try:
                opponent_team_name = user['metadata']['team_name']
            except:
                opponent_team_name = user['display_name']
            if "https://" in user['avatar']:
                opponent_avatar = user['avatar']
            else:
                opponent_avatar = 'https://sleepercdn.com/avatars/'+user['avatar']

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
    for player in trending:
        player_name = []
        name = (data[player]['full_name'])
        player_name.append(name)
        player_name.append('prospect')
        player_names.append(player_name)

    big_games = []
    opponent_big_games = []
    prospects = []
    bench = []

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
                    fgm = log['FGM'] * fgm_setting
                    fgmi = (log['FGA'] - log['FGM']) * fgmi_setting
                    ftm = log['FTM'] * ftm_setting
                    ftmi = (log['FTA'] - log['FTM']) * ftmi_setting
                    threes = log['FG3M'] * threes_setting
                    dd = log['DD2'] * dd_setting
                    td = log['TD3'] * td_setting
                    if log['PTS'] > 39:
                        bonus_pt_40p = bonus_pts40_setting
                    else:
                        bonus_pt_40p = 0
                    if log['PTS'] > 49:
                        bonus_pt_50p = bonus_pts50_setting
                    else:
                        bonus_pt_50p = 0
                    if log['AST'] > 14:
                        bonus_ast_15p = bonus_ast15_setting
                    else:
                        bonus_ast_15p = 0
                    if log['REB'] > 19:
                        bonus_reb_20p = bonus_reb20_setting
                    else:
                        bonus_reb_20p = 0
                    
                    fantasypoints = round(pts + ast + reb + stl + blk + to + fgm + fgmi + ftm + ftmi + threes + dd + td + bonus_pt_40p + bonus_pt_50p + bonus_ast_15p + bonus_reb_20p, 1)

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
                            fgm_last3 = log['FGM'] * fgm_setting
                            fgmi_last3 = (log['FGA'] - log['FGM']) * fgmi_setting
                            ftm_last3 = log['FTM'] * ftm_setting
                            ftmi_last3 = (log['FTA'] - log['FTM']) * ftmi_setting
                            threes_last3 = log['FG3M'] * threes_setting
                            dd_last3 = log['DD2'] * dd_setting / gamesplayed
                            td_last3 = log['TD3'] * td_setting / gamesplayed
                            if log['PTS'] > 39:
                                bonus_pt_40p_last3 = bonus_pts40_setting
                            else:
                                bonus_pt_40p_last3 = 0
                            if log['PTS'] > 49:
                                bonus_pt_50p_last3 = bonus_pts50_setting
                            else:
                                bonus_pt_50p_last3 = 0
                            if log['AST'] > 14:
                                bonus_ast_15p_last3 = bonus_ast15_setting
                            else:
                                bonus_ast_15p_last3 = 0
                            if log['REB'] > 19:
                                bonus_reb_20p_last3 = bonus_reb20_setting
                            else:
                                bonus_reb_20p_last3 = 0                     

                            fplast3 = round(pts_last3 + ast_last3 + reb_last3 + stl_last3 + blk_last3 + to_last3 + fgm_last3 + fgmi_last3 + ftm_last3 + ftmi_last3 + threes_last3 + dd_last3 + td_last3 + bonus_pt_40p_last3 + bonus_pt_50p_last3 + bonus_ast_15p_last3 + bonus_reb_20p_last3, 1)
                            
                            percentdiff = int(round((fantasypoints - fplast3) / fplast3 * 100, 0))
                            if percentdiff < 0:
                                change = 'lower'
                            else:
                                change = 'higher'

                            if (percentdiff > 20 and fantasypoints > good_game_alert_fantasy_points and player[1] != 'prospect') or (fantasypoints > huge_game_alert_fantasy_points) or (fplast3 > prospect_alert_fantasy_points and fantasypoints > prospect_alert_fantasy_points and minutes > 24 and player[1] == 'prospect') or (fantasypoints > prospect_alert_fantasy_points and minutes > 28 and player[1] == 'prospect'):
                                fantasypointsstr = str(fantasypoints)
                                percentdiffstr = str(percentdiff)
                                gamesplayedstr = str(gamesplayed)
                                fplast3str = str(fplast3)
                                minutestr = str(minutes)

                                alert = {}
                                empty_alert = {'name':'\a','value':'\u200b'}

                                if player[1] == 'myteam':
                                    if len(player) == 3:
                                        player_name = player[2]
                                    alert_string = f'- {fantasypointsstr} points\n- {percentdiffstr}% {change} than last {gamesplayedstr} game avg of {fplast3str}'
                                    alert["name"] = player_name
                                    alert["value"] = alert_string
                                    big_games.append(empty_alert)
                                    big_games.append(alert)

                                elif player[1] == 'opponent':
                                    alert_string = f"- {fantasypointsstr} points\n- {percentdiffstr}% {change} than last {gamesplayedstr} game avg of {fplast3str}"
                                    alert["name"] = player_name
                                    alert["value"] = alert_string
                                    opponent_big_games.append(empty_alert)
                                    opponent_big_games.append(alert)
                                
                                elif player[1] == 'prospect':
                                    alert_string = f"- {fantasypointsstr} points\n- {minutestr} MPG\n- {percentdiffstr}% {change} than last {gamesplayedstr} game avg of {fplast3str}"
                                    alert["name"] = player_name
                                    alert["value"] = alert_string
                                    prospects.append(empty_alert)
                                    prospects.append(alert)

                                print(alert)

                            else:
                                print(player_name+' done')

        else:
            print(player_name+' not found')


    for player in reserve_players:
        for game in games:
            if player[1] == game['home_team']['abbreviation'] or player[1] == game['visitor_team']['abbreviation']:
                if game['period'] == 0:
                    gamestart_utc = game['status']
                    stamp = datetime.strptime(gamestart_utc, '%Y-%m-%dT%H:%M:%SZ')
                    final_time = stamp - timedelta(hours=time_offset+3)
                    gamestart = final_time.strftime("%I:%M %p")
                    if gamestart[0] == '0':
                        gamestartfinal = gamestart[1:]
                    else:
                        gamestartfinal = gamestart
                    
                    alert = {}
                    alert_string = f'Game today at {gamestartfinal}'
                    player_name = player[0]
                    alert["name"] = player_name
                    alert["value"] = alert_string
                    bench.append(empty_alert)
                    bench.append(alert)

                    print(alert)

    big_game_dict = {'author':{'name':'\a', 'icon_url':user_avatar}, 'title':'__**'+team_name+'**__', 'color':2281805, 'fields':big_games}
    opponent_big_games_dict = {'author':{'name':'\a', 'icon_url':opponent_avatar}, 'title':'__**'+opponent_team_name+'**__', 'color':13705777, 'fields':opponent_big_games}
    prospects_dict = {'title':'__**Prospects**__', 'color':8921809, 'fields':prospects}
    bench_dict = {'title':'__**Bench**__', 'color':13746722, 'fields':bench}

    embeds = [big_game_dict, opponent_big_games_dict, prospects_dict, bench_dict]
    report = {}
    report["username"] = leaguename
    report["avatar_url"] = league_avatar
    report["embeds"] = embeds
    result = requests.post(webhook_url, json=report)

    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")