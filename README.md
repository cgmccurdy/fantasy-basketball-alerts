# fantasy-basketball-alerts

Works with Sleeper. Enter your Sleeper username and IFTTT key in the python file.  

To get an IFTTT key, sign-up for an IFTTT account. Retrieve your key from the link below by clicking on "Documentation".  
https://ifttt.com/maker_webhooks  

Alerts will generate for:  
- Big games from players on your team  
- Big games from players on matchup's team  
- Big games from available trending players  
- A player on the bench who has a game that day  

Supported scoring settings: PTS, REB, AST, STL, BLK, TOV, Double Doubles, Triple Doubles.  
Player cache refreshed every 7 days.  

IFTTT Setup:  
- Create an applet  
- For "If" choose "Webhooks" and select "receive a web request"  
- Enter "sleeper_alert" as the Event Name  
- For "Then" choose "Notifcations" and select "Send a rich notification from the IFTTT app"  
- For Message use "Add Ingredient" to input "Value1"  
- For Title use "Add Ingredient" to input "Value2"  
- For Link URL input "sleeperbot://" (This is for iOS. I'm not sure what the URL to open the Sleeper app is on Android.)  
- For Image URL use "Add Ingredient" to input "Value3"  

Use Windows Task Scheduler or Cron on Mac to automate running the script daily:  
https://towardsdatascience.com/how-to-easily-automate-your-python-scripts-on-mac-and-windows-459388c9cc94
