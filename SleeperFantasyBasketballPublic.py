import requests
import os
import json
import time
from datetime import datetime, date, timedelta

# Enter your Sleeper username
# Set time_offset to 0 for ET, 1 for CT, 2 for MT, 3 for PT
# Set ir_notifcations to True to receive notifications for players in IR slots

user_name = 'enter_username'
IFTTT = 'enter_IFTTT_key'
time_offset = 1
ir_notifcations = False

def ifttt(first, second):
    report = {}
    report["value1"] = first
    report["value2"] = second
    requests.post("https://maker.ifttt.com/trigger/sleeper_alert/with/key/"+IFTTT, data=report) 

today = date.today()
yesterday  = today - timedelta(days = 1)
yesterdayformat = yesterday.strftime("%m/%d/%Y")

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

state = requests.get("https://api.sleeper.app/v1/state/nba").json()
season = state['season']
week = str(state['week'])

user = requests.get("https://api.sleeper.app/v1/user/"+user_name).json()
userid = user['user_id']

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

    leaguerosters = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/rosters").json()
    for rosters in leaguerosters:
        owner_id = rosters['owner_id']
        if owner_id == userid:
            roster_id = rosters['roster_id']
            roster = rosters['players']
            starters = rosters['starters']
            ir = rosters['reserve']
            if ir_notifcations == True:
                reserves = list(set(starters).symmetric_difference(set(roster)))
            else:
                reserves_ir = list(set(starters).symmetric_difference(set(roster)))
                reserves = list(set(ir).symmetric_difference(set(reserves_ir)))

    leaguematchups = requests.get("https://api.sleeper.app/v1/league/"+leagueid+"/matchups/"+week).json()
    for matchup in leaguematchups:
        if roster_id == matchup['roster_id']:
            matchup_id = matchup['matchup_id']
    for matchup in leaguematchups:
        if matchup_id == matchup['matchup_id'] and roster_id != matchup['roster_id']:
            opponent_roster = matchup['starters']
            opponent_id = matchup['roster_id']

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

    from nba_api.stats.static import players
    from nba_api.stats.endpoints import playergamelog
    from nba_api.stats.library.parameters import Season
    from nba_api.stats.endpoints import playerdashboardbylastngames

    for player in player_names:
        player_name = player[0]
        id = players.find_players_by_full_name(player_name)[0]['id']
        data = playergamelog.PlayerGameLog(player_id=id,season=Season.current_season,date_from_nullable=yesterdayformat).get_normalized_json()
        json_object = json.loads(data)
        length = len(json_object['PlayerGameLog'])
        time.sleep(0.5)
        if length > 0:
            pts_raw = json_object['PlayerGameLog'][0]['PTS']
            ast_raw = json_object['PlayerGameLog'][0]['AST']
            reb_raw = json_object['PlayerGameLog'][0]['REB']
            pts = pts_raw * pts_setting
            ast = ast_raw * ast_setting
            reb = reb_raw * reb_setting
            stl = json_object['PlayerGameLog'][0]['STL'] * stl_setting
            blk = json_object['PlayerGameLog'][0]['BLK'] * blk_setting
            to = json_object['PlayerGameLog'][0]['TOV'] * to_setting
            if pts_raw > 9 and ast_raw > 9:
                dd = dd_setting
            elif pts_raw > 9 and reb_raw > 9:
                dd = dd_setting
            elif ast_raw > 9 and reb_raw > 9:
                dd = dd_setting
            else:
                dd = 0
            if pts_raw > 9 and ast_raw > 9 and reb_raw > 9:
                td = td_setting
            else:
                td = 0
            
            fantasypoints = pts + ast + reb + stl + blk + to + dd + td

            data = playerdashboardbylastngames.PlayerDashboardByLastNGames(player_id=id,season=Season.current_season,last_n_games=5,per_mode_detailed='PerGame').get_normalized_json()
            json_object = json.loads(data)
            gamesplayed = json_object['Last5PlayerDashboard'][0]['GP']
            pts_raw_last5 = json_object['Last5PlayerDashboard'][0]['PTS']
            ast_raw_last5 = json_object['Last5PlayerDashboard'][0]['AST']
            reb_raw_last5 = json_object['Last5PlayerDashboard'][0]['REB']
            pts_last5 = pts_raw_last5 * pts_setting
            ast_last5 = ast_raw_last5 * ast_setting
            reb_last5 = reb_raw_last5 * reb_setting
            stl_last5 = json_object['Last5PlayerDashboard'][0]['STL'] * stl_setting
            blk_last5 = json_object['Last5PlayerDashboard'][0]['BLK'] * blk_setting
            to_last5 = json_object['Last5PlayerDashboard'][0]['TOV'] * to_setting
            if pts_raw_last5 > 9 and ast_raw_last5 > 9:
                dd_last5 = dd_setting
            elif pts_raw_last5 > 9 and reb_raw_last5 > 9:
                dd_last5 = dd_setting
            elif ast_raw_last5 > 9 and reb_raw_last5 > 9:
                dd_last5 = dd_setting
            else:
                dd_last5 = 0
            if pts_raw_last5 > 9 and ast_raw_last5 > 9 and reb_raw_last5 > 9:
                td_last5 = td_setting
            else:
                td_last5 = 0

            fplast5 = round(pts_last5 + ast_last5 + reb_last5 + stl_last5 + blk_last5 + to_last5 + dd_last5 + td_last5, 0)
            
            percentdiff = round((fantasypoints - fplast5) / fplast5 * 100, 1)

            print(player_name+' finished')

            if percentdiff > 25 and fantasypoints > 35:
                fantasypointsstr = str(fantasypoints)
                percentdiffstr = str(percentdiff)
                gamesplayedstr = str(gamesplayed)
                fplast5str = str(fplast5)

                if player[1] == 'myteam':
                    alert = 'Great game from '+player_name+' with '+fantasypointsstr+' points! '+percentdiffstr+'% higher than his last '+gamesplayedstr+' game average of '+fplast5str+'.'
                else:
                    alert = "Oof! "+player_name+" on your opponent's team dropped "+fantasypointsstr+" points. "+percentdiffstr+"% higher than his last "+gamesplayedstr+" game average of "+fplast5str+"."
                
                print(alert)
                ifttt(leaguename, alert)


    today_str = str(today)
    data = requests.get("https://www.balldontlie.io/api/v1/games?start_date="+today_str+"&end_date="+today_str).json()
    games = data['data']

    for player in reserve_players:
        for game in games:
            if player[1] == game['home_team']['abbreviation'] or player[1] == game['visitor_team']['abbreviation']:
                gamestart_est = game['status']
                print(gamestart_est)
                stamp = datetime.strptime(gamestart_est[:-3], "%I:%M %p")
                final_time = stamp - timedelta(hours=time_offset)
                gamestart = final_time.strftime("%I:%M %p")
                if gamestart[0] == '0':
                    gamestartfinal = gamestart[1:]
                else:
                    gamestartfinal = gamestart
                
                alert = player[0]+' is on the bench and has a game today at '+gamestartfinal+'.'

                print(alert)
                ifttt(leaguename, alert)