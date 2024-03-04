# fantasy-basketball-alerts

Works with Sleeper. Enter your Sleeper username and Discord webhook URL in the python file.  

To get a Discord webhook URL, go to Server Settings, Integrations, and Create Webhook:  
https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks

Alerts will generate for:  
- Big games from players on your team  
- Big games from players on matchup's team  
- Big games from available trending players  
- A player on the bench who has a game that day  

Supported scoring settings: PTS, REB, AST, STL, BLK, TOV, Double Doubles, Triple Doubles.  
Player cache refreshed every 7 days.  

Use Windows Task Scheduler or Cron on Mac to automate running the script daily:  
https://towardsdatascience.com/how-to-easily-automate-your-python-scripts-on-mac-and-windows-459388c9cc94
