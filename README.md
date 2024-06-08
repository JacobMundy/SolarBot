# Discord Bot
## Setup


* ### Create new application in discord developer portal
![Create new application](img/ApplicationPage.png)

* ### Select the bot section and create a new token 
  * ### Keep the token secret, do not share it with anyone
  
![Create new token](img/BotPage.png)

* ### Below the token you should also select all the intents

![Select all intents](img/IntentsPage.png)

* ### Now Select the OAuth2 Section to setup the bot invite link
  * ### Select the bot scope
  * ### Select the permissions
    * ### Only select permissions that you want the bot to have at the very least it should be allowed to send and read messages and the admin commands will need specific permissions such as manage messages
  * ### Copy the link and paste it in your browser to invite the bot to your server

![Select the bot Scope](img/ScopePage.png)
![Select the bot permissions](img/PermissionsPage.png)
![Copy the link](img/URLPage.png)

* ### Now you can clone the repository and create a .env file in the root directory
  * ### Add the following to the .env file replacing the {YOUR_TOKEN} with the token you copied earlier
    * ### DISCORD_TOKEN={YOUR_TOKEN}

* ### All you need to do now is install the required packages and run the bot
  * ### If you have the discord pip package installed you will need to uninstall it as it conflicts with py-cord, discord.py is fine though
  * ### Run the following command in the terminal
    * ### `pip install -r requirements.txt`
  * ### Run the bot
    * ### `python main.py`