import os

from discord.ext import commands as cmds

from src.basicbot import BasicBot
from src.cogs import *

heroku = BasicBot(command_prefix=cmds.when_mentioned_or("!"))

heroku.add_cog(Commands(heroku))
heroku.add_cog(CustomCommands(heroku, db_url=os.environ["DATABASE_URL"]))
heroku.add_cog(Greetings(heroku, db_url=os.environ["DATABASE_URL"]))
heroku.add_cog(Notifications(heroku, db_url=os.environ["DATABASE_URL"]))
heroku.add_cog(Roles(heroku, db_url=os.environ["DATABASE_URL"]))
heroku.add_cog(Reminders(heroku, db_url=os.environ["DATABASE_URL"]))

heroku.run(os.environ["TOKEN"])
