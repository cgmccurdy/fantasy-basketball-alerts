# fantasy-basketball-alerts

Currently works with Sleeper. Enter your Sleeper username and IFTTT key in the script.  
Supported scoring settings: PTS, REB, AST, STL, BLK, TOV, Double Doubles, Triple Doubles.

To get an IFTTT key, sign-up for an IFTTT account. Retrieve your key from the link below by clicking on "Documentation".  
https://ifttt.com/maker_webhooks

In IFTTT, you will need to create an applet.  
For "If" choose "Webhooks" and select "receive a web request".  
Enter "sleeper_alert" as the Event Name.  
For "Then" choose "Notifcations" and select "Send a rich notification from the IFTTT app".  
For Message use "Add Ingredient" to input "Value2"  
For Title use "Add Ingredient" to input "Value1"  
For Link URL input "https://sleeper.com" (Trying to figure out a URL that will open the Sleeper app directly)

Use Windows Task Scheduler or Cron on Mac to automate running the script daily:  
https://towardsdatascience.com/how-to-easily-automate-your-python-scripts-on-mac-and-windows-459388c9cc94
